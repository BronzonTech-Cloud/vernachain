import asyncio
import json
import time
from typing import Dict, List, Optional, Set, Any, Callable
from nacl.public import PrivateKey, PublicKey, Box
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
import struct


class Node:
    """Represents a network node with its cryptographic identities."""
    def __init__(self, host: str, port: int):
        # Network info
        self.host = host
        self.port = port
        
        # Encryption keys (for message encryption)
        self._private_key = PrivateKey.generate()
        self.public_key = self._private_key.public_key
        
        # Signing keys (for message authentication)
        self._signing_key = SigningKey.generate()
        self.verify_key = self._signing_key.verify_key
        
        # Node ID for DHT (derived from public key)
        self.node_id = self.public_key.encode(encoder=HexEncoder)
        
    def create_box(self, peer_public_key: PublicKey) -> Box:
        """Create an encryption box for communicating with a peer."""
        return Box(self._private_key, peer_public_key)


class Message:
    """Network message with encryption and authentication."""
    TYPES = {
        'PING': 0,
        'PONG': 1,
        'FIND_NODE': 2,
        'NODES_FOUND': 3,
        'STORE': 4,
        'FIND_VALUE': 5,
        'VALUE_FOUND': 6,
        'BROADCAST': 7
    }
    
    def __init__(self, msg_type: str, payload: Dict[str, Any], sender: Node):
        self.type = msg_type
        self.payload = payload
        self.sender = sender
        self.timestamp = time.time()
        
    def serialize(self, box: Box) -> bytes:
        """Serialize and encrypt message."""
        # Create message structure
        message = {
            'type': self.TYPES[self.type],
            'payload': self.payload,
            'sender': {
                'host': self.sender.host,
                'port': self.sender.port,
                'public_key': self.sender.public_key.encode(encoder=HexEncoder).decode(),
                'verify_key': self.sender.verify_key.encode(encoder=HexEncoder).decode()
            },
            'timestamp': self.timestamp
        }
        
        # Sign the message
        message_bytes = json.dumps(message).encode()
        signature = self.sender._signing_key.sign(message_bytes)
        
        # Encrypt the message and signature
        encrypted = box.encrypt(message_bytes + signature)
        
        # Add length prefix for framing
        length = struct.pack('!I', len(encrypted))
        return length + encrypted
        
    @classmethod
    def deserialize(cls, data: bytes, box: Box, verify_key: VerifyKey) -> 'Message':
        """Decrypt and deserialize message."""
        # Decrypt message
        decrypted = box.decrypt(data)
        
        # Split message and signature
        message_bytes = decrypted[:-64]  # Last 64 bytes are signature
        signature = decrypted[-64:]
        
        # Verify signature
        verify_key.verify(message_bytes, signature)
        
        # Parse message
        message = json.loads(message_bytes.decode())
        
        # Create sender node
        sender = Node(message['sender']['host'], message['sender']['port'])
        sender.public_key = PublicKey(message['sender']['public_key'].encode(), encoder=HexEncoder)
        sender.verify_key = VerifyKey(message['sender']['verify_key'].encode(), encoder=HexEncoder)
        
        # Get message type
        msg_type = next(k for k, v in cls.TYPES.items() if v == message['type'])
        
        # Create message instance
        msg = cls(msg_type, message['payload'], sender)
        msg.timestamp = message['timestamp']
        return msg


class KademliaTable:
    """Kademlia routing table implementation."""
    K = 20  # Max nodes per bucket
    
    def __init__(self, node: Node):
        self.node = node
        self.buckets: List[Set[Node]] = [set() for _ in range(256)]  # 256-bit IDs
        
    def get_bucket_index(self, node_id: bytes) -> int:
        """Calculate appropriate bucket index for a node."""
        distance = int.from_bytes(node_id, 'big') ^ int.from_bytes(self.node.node_id, 'big')
        return (distance.bit_length() - 1) if distance > 0 else 0
        
    def add_node(self, node: Node) -> bool:
        """Add a node to the appropriate bucket."""
        if node.node_id == self.node.node_id:
            return False
            
        bucket_index = self.get_bucket_index(node.node_id)
        bucket = self.buckets[bucket_index]
        
        if node in bucket:
            # Move node to end (most recently seen)
            bucket.remove(node)
            bucket.add(node)
            return True
            
        if len(bucket) < self.K:
            bucket.add(node)
            return True
            
        return False
        
    def get_closest_nodes(self, target_id: bytes, k: int = K) -> List[Node]:
        """Get k closest nodes to a target ID."""
        nodes = []
        
        # Calculate distances to all nodes
        for bucket in self.buckets:
            for node in bucket:
                distance = int.from_bytes(node.node_id, 'big') ^ int.from_bytes(target_id, 'big')
                nodes.append((distance, node))
                
        # Sort by distance and return k closest
        nodes.sort(key=lambda x: x[0])
        return [node for _, node in nodes[:k]]


class NetworkProtocol:
    """Advanced networking protocol implementation."""
    def __init__(self, node: Node):
        self.node = node
        self.routing_table = KademliaTable(node)
        self.message_handlers: Dict[str, Callable] = {}
        self.server: Optional[asyncio.AbstractServer] = None
        self.peers: Dict[str, Node] = {}  # node_id -> Node
        self.boxes: Dict[str, Box] = {}  # node_id -> Box
        
    async def start(self):
        """Start the network protocol."""
        self.server = await asyncio.start_server(
            self._handle_connection,
            self.node.host,
            self.node.port
        )
        
        # Register default message handlers
        self.message_handlers.update({
            'PING': self._handle_ping,
            'PONG': self._handle_pong,
            'FIND_NODE': self._handle_find_node,
            'NODES_FOUND': self._handle_nodes_found
        })
        
        print(f"Node listening on {self.node.host}:{self.node.port}")
        
    async def stop(self):
        """Stop the network protocol."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
    async def connect(self, host: str, port: int):
        """Connect to a peer node."""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Exchange node information
            await self._handshake(reader, writer)
            
            # Start message handling loop
            asyncio.create_task(self._handle_messages(reader, writer))
            
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    async def _handshake(self, reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        """Perform cryptographic handshake with peer."""
        # Send our node info
        node_info = {
            'host': self.node.host,
            'port': self.node.port,
            'public_key': self.node.public_key.encode(encoder=HexEncoder).decode(),
            'verify_key': self.node.verify_key.encode(encoder=HexEncoder).decode()
        }
        writer.write(json.dumps(node_info).encode() + b'\n')
        await writer.drain()
        
        # Receive peer's node info
        peer_info = json.loads((await reader.readline()).decode())
        
        # Create peer node
        peer = Node(peer_info['host'], peer_info['port'])
        peer.public_key = PublicKey(peer_info['public_key'].encode(), encoder=HexEncoder)
        peer.verify_key = VerifyKey(peer_info['verify_key'].encode(), encoder=HexEncoder)
        
        # Store peer information
        self.peers[peer.node_id] = peer
        self.boxes[peer.node_id] = self.node.create_box(peer.public_key)
        self.routing_table.add_node(peer)
        
    async def _handle_connection(self, reader: asyncio.StreamReader,
                               writer: asyncio.StreamWriter):
        """Handle incoming connection."""
        try:
            # Perform handshake
            await self._handshake(reader, writer)
            
            # Handle messages
            await self._handle_messages(reader, writer)
            
        except Exception as e:
            print(f"Connection handler error: {e}")
            writer.close()
            await writer.wait_closed()
            
    async def _handle_messages(self, reader: asyncio.StreamReader,
                             writer: asyncio.StreamWriter):
        """Handle incoming messages from a peer."""
        try:
            while True:
                # Read message length
                length_bytes = await reader.readexactly(4)
                length = struct.unpack('!I', length_bytes)[0]
                
                # Read message data
                data = await reader.readexactly(length)
                
                # Get peer info
                peer_address = writer.get_extra_info('peername')
                peer = next(p for p in self.peers.values()
                          if (p.host, p.port) == peer_address)
                
                # Decrypt and process message
                box = self.boxes[peer.node_id]
                message = Message.deserialize(data, box, peer.verify_key)
                
                # Handle message
                if message.type in self.message_handlers:
                    response = await self.message_handlers[message.type](message)
                    if response:
                        writer.write(response.serialize(box))
                        await writer.drain()
                        
        except asyncio.IncompleteReadError:
            # Connection closed
            pass
        except Exception as e:
            print(f"Message handler error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            
    async def send_message(self, peer: Node, msg_type: str,
                          payload: Dict[str, Any]) -> Optional[Message]:
        """Send a message to a peer and wait for response."""
        try:
            # Connect if not already connected
            if peer.node_id not in self.peers:
                if not await self.connect(peer.host, peer.port):
                    return None
                    
            # Create and send message
            message = Message(msg_type, payload, self.node)
            box = self.boxes[peer.node_id]
            
            reader, writer = await asyncio.open_connection(peer.host, peer.port)
            writer.write(message.serialize(box))
            await writer.drain()
            
            # Read response
            length_bytes = await reader.readexactly(4)
            length = struct.unpack('!I', length_bytes)[0]
            data = await reader.readexactly(length)
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Process response
            return Message.deserialize(data, box, peer.verify_key)
            
        except Exception as e:
            print(f"Send message failed: {e}")
            return None
            
    async def broadcast(self, msg_type: str, payload: Dict[str, Any]):
        """Broadcast a message to all peers."""
        for peer in self.peers.values():
            asyncio.create_task(self.send_message(peer, msg_type, payload))
            
    async def _handle_ping(self, message: Message) -> Message:
        """Handle ping message."""
        return Message('PONG', {}, self.node)
        
    async def _handle_pong(self, message: Message) -> None:
        """Handle pong message."""
        return None
        
    async def _handle_find_node(self, message: Message) -> Message:
        """Handle find_node message."""
        target_id = message.payload['target_id'].encode()
        closest_nodes = self.routing_table.get_closest_nodes(target_id)
        
        nodes_info = [{
            'host': node.host,
            'port': node.port,
            'node_id': node.node_id.decode()
        } for node in closest_nodes]
        
        return Message('NODES_FOUND', {'nodes': nodes_info}, self.node)
        
    async def _handle_nodes_found(self, message: Message) -> None:
        """Handle nodes_found message."""
        for node_info in message.payload['nodes']:
            # Connect to new nodes
            if node_info['node_id'] not in self.peers:
                asyncio.create_task(
                    self.connect(node_info['host'], node_info['port'])
                )
        return None 