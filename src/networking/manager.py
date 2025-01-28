import asyncio
from typing import Dict, List, Optional, Any, Set, Callable
from .protocol import Node, NetworkProtocol
import random


class NetworkManager:
    """Manages high-level networking operations."""
    
    def __init__(self, host: str, port: int, bootstrap_nodes: Optional[List[Dict[str, Any]]] = None):
        self.node = Node(host, port)
        self.protocol = NetworkProtocol(self.node)
        self.bootstrap_nodes = bootstrap_nodes or []
        self.message_callbacks: Dict[str, Set[Callable]] = {}
        self.running = False
        
    async def start(self):
        """Start the network manager."""
        if self.running:
            return
            
        # Start network protocol
        await self.protocol.start()
        self.running = True
        
        # Connect to bootstrap nodes
        for node_info in self.bootstrap_nodes:
            asyncio.create_task(
                self.protocol.connect(node_info['host'], node_info['port'])
            )
            
        # Start maintenance tasks
        asyncio.create_task(self._maintenance_loop())
        
    async def stop(self):
        """Stop the network manager."""
        if not self.running:
            return
            
        self.running = False
        await self.protocol.stop()
        
    def register_message_handler(self, msg_type: str, callback: callable):
        """Register a callback for a message type."""
        if msg_type not in self.message_callbacks:
            self.message_callbacks[msg_type] = set()
        self.message_callbacks[msg_type].add(callback)
        
    def unregister_message_handler(self, msg_type: str, callback: callable):
        """Unregister a message callback."""
        if msg_type in self.message_callbacks:
            self.message_callbacks[msg_type].discard(callback)
            
    async def broadcast_message(self, msg_type: str, payload: Dict[str, Any]):
        """Broadcast a message to the network."""
        await self.protocol.broadcast(msg_type, payload)
        
    async def find_node(self, target_id: bytes) -> List[Node]:
        """Find nodes closest to a target ID."""
        # First check local routing table
        closest = self.protocol.routing_table.get_closest_nodes(target_id)
        if not closest:
            return []
            
        # Ask closest nodes for their closest nodes
        queried_nodes = set()
        for node in closest:
            if node.node_id in queried_nodes:
                continue
                
            queried_nodes.add(node.node_id)
            response = await self.protocol.send_message(
                node,
                'FIND_NODE',
                {'target_id': target_id.decode()}
            )
            
            if response and response.type == 'NODES_FOUND':
                for node_info in response.payload['nodes']:
                    if node_info['node_id'] not in queried_nodes:
                        # Connect to new nodes
                        await self.protocol.connect(
                            node_info['host'],
                            node_info['port']
                        )
                        
        # Return updated closest nodes
        return self.protocol.routing_table.get_closest_nodes(target_id)
        
    async def store_value(self, key: str, value: Any) -> bool:
        """Store a value in the DHT."""
        # Find nodes to store the value
        key_hash = self.protocol._encode_key(key)
        nodes = await self.find_node(key_hash)
        
        if not nodes:
            return False
            
        # Store value on each node
        success = False
        for node in nodes:
            response = await self.protocol.send_message(
                node,
                'STORE',
                {
                    'key': key,
                    'value': value
                }
            )
            if response:
                success = True
                
        return success
        
    async def get_value(self, key: str) -> Optional[Any]:
        """Retrieve a value from the DHT."""
        # Find nodes that might have the value
        key_hash = self.protocol._encode_key(key)
        nodes = await self.find_node(key_hash)
        
        if not nodes:
            return None
            
        # Query nodes for the value
        for node in nodes:
            response = await self.protocol.send_message(
                node,
                'FIND_VALUE',
                {'key': key}
            )
            
            if response and response.type == 'VALUE_FOUND':
                return response.payload.get('value')
                
        return None
        
    async def _maintenance_loop(self):
        """Periodic maintenance tasks."""
        while self.running:
            try:
                # Ping random nodes to keep connections alive
                for peer in list(self.protocol.peers.values()):
                    if random.random() < 0.2:  # 20% chance to ping each peer
                        response = await self.protocol.send_message(
                            peer,
                            'PING',
                            {}
                        )
                        
                        if not response:
                            # Remove dead peer
                            peer_id = peer.node_id
                            if peer_id in self.protocol.peers:
                                del self.protocol.peers[peer_id]
                            if peer_id in self.protocol.boxes:
                                del self.protocol.boxes[peer_id]
                                
                # Refresh random bucket
                bucket_idx = random.randrange(256)
                bucket = self.protocol.routing_table.buckets[bucket_idx]
                if bucket:
                    # Find nodes for random key in bucket range
                    target_id = random.randbytes(32)  # 256 bits
                    await self.find_node(target_id)
                    
            except Exception as e:
                print(f"Maintenance error: {e}")
                
            await asyncio.sleep(60)  # Run maintenance every minute
            
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        total_buckets = sum(1 for b in self.protocol.routing_table.buckets if b)
        total_nodes = sum(len(b) for b in self.protocol.routing_table.buckets)
        
        return {
            'node_id': self.node.node_id.decode(),
            'address': f"{self.node.host}:{self.node.port}",
            'peers': len(self.protocol.peers),
            'active_buckets': total_buckets,
            'known_nodes': total_nodes
        } 