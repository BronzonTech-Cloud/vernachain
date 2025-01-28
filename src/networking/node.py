"""Node implementation for Vernachain P2P network."""

import json
import socket
import threading
from typing import Dict, Any, Set, Optional
from dataclasses import dataclass, field
from ..blockchain.blockchain import Blockchain
from ..blockchain.block import Block
from ..blockchain.transaction import Transaction
from src.utils.crypto import verify_signature
from src.utils.validation import is_valid_transaction, is_valid_block
from src.utils.serialization import serialize_transaction, deserialize_transaction
from src.utils.logging import networking_logger


@dataclass
class Node:
    host: str = 'localhost'
    port: int = 5000
    bootstrap_host: Optional[str] = None
    bootstrap_port: Optional[int] = None
    peers: Set[tuple] = field(default_factory=set)
    running: bool = False
    
    def __post_init__(self):
        """Initialize additional attributes after dataclass initialization."""
        self.blockchain = Blockchain()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Enable address reuse to prevent "Address already in use" errors
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        networking_logger.info(f"Node initialized at {self.host}:{self.port}")
        
        # Connect to bootstrap node if provided
        if self.bootstrap_host and self.bootstrap_port:
            self._connect_to_bootstrap_node()

    def start(self) -> None:
        """Start the node's server and listening thread."""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            # Start listening thread
            listener_thread = threading.Thread(target=self._listen_for_connections)
            listener_thread.daemon = True
            listener_thread.start()
            
            networking_logger.info(f"Node started listening on {self.host}:{self.port}")
            
        except Exception as e:
            networking_logger.error(f"Failed to start node: {e}")
            self.running = False

    def _connect_to_bootstrap_node(self) -> None:
        """Connect to the bootstrap node and get initial peer list."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.bootstrap_host, self.bootstrap_port))
                
                # Register with bootstrap node
                self._send_message(sock, {
                    "type": "register",
                    "host": self.host,
                    "port": self.port
                })
                
                # Receive peer list
                if response := self._receive_message(sock):
                    if response["type"] == "peers":
                        # Connect to each peer
                        for peer_host, peer_port in response["peers"]:
                            if (peer_host, peer_port) != (self.host, self.port):
                                self.connect_to_peer(peer_host, peer_port)
                
                networking_logger.info("Successfully connected to bootstrap node")
                
        except Exception as e:
            networking_logger.error(f"Failed to connect to bootstrap node: {e}")

    def stop(self) -> None:
        """Stop the node's server."""
        self.running = False
        self.socket.close()
        networking_logger.info("Node stopped")

    def connect_to_peer(self, peer_host: str, peer_port: int) -> bool:
        """
        Connect to a new peer.
        
        Args:
            peer_host: Peer's host address
            peer_port: Peer's port
            
        Returns:
            bool: True if connection successful
        """
        if (peer_host, peer_port) in self.peers:
            return True

        try:
            # Try to connect to peer
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_host, peer_port))
            
            # Send handshake message
            self._send_message(sock, {
                "type": "handshake",
                "host": self.host,
                "port": self.port
            })
            
            # Add peer to list
            self.peers.add((peer_host, peer_port))
            
            # Start peer handler thread
            handler_thread = threading.Thread(
                target=self._handle_peer,
                args=(sock, (peer_host, peer_port))
            )
            handler_thread.daemon = True
            handler_thread.start()
            
            # Request latest blockchain state
            self._send_message(sock, {
                "type": "get_blockchain"
            })
            
            return True
        except Exception as e:
            networking_logger.error(f"Failed to connect to peer {peer_host}:{peer_port}: {e}")
            return False

    def broadcast_transaction(self, transaction: Transaction) -> None:
        """
        Broadcast a transaction to all peers.
        
        Args:
            transaction: Transaction to broadcast
        """
        if not is_valid_transaction(transaction):
            networking_logger.error("Invalid transaction, not broadcasting")
            return
            
        tx_data = serialize_transaction(transaction)
        message = {
            'type': 'transaction',
            'data': tx_data
        }
        
        self._broadcast_to_peers(message)
        networking_logger.debug(f"Transaction broadcast to {len(self.peers)} peers")

    def broadcast_block(self, block: Block) -> None:
        """
        Broadcast a block to all peers.
        
        Args:
            block: Block to broadcast
        """
        if not is_valid_block(block, self.blockchain.get_latest_block()):
            networking_logger.error("Invalid block, not broadcasting")
            return
            
        message = {
            'type': 'block',
            'data': block.to_dict()
        }
        
        self._broadcast_to_peers(message)
        networking_logger.debug(f"Block broadcast to {len(self.peers)} peers")

    def _listen_for_connections(self) -> None:
        """Listen for incoming peer connections."""
        while self.running:
            try:
                client_sock, address = self.socket.accept()
                networking_logger.info(f"New connection from {address[0]}:{address[1]}")
                
                # Start client handler thread
                handler_thread = threading.Thread(
                    target=self._handle_peer,
                    args=(client_sock, address)
                )
                handler_thread.daemon = True
                handler_thread.start()
            except Exception as e:
                if self.running:
                    networking_logger.error(f"Error accepting connection: {e}")

    def _handle_peer(self, peer_socket: socket.socket, address: tuple) -> None:
        """
        Handle communication with a peer.
        
        Args:
            peer_socket: Socket connected to peer
            address: Peer's address tuple (host, port)
        """
        try:
            while self.running:
                if message := self._receive_message(peer_socket):
                    self._handle_message(message, peer_socket)
                else:
                    break
        except Exception as e:
            networking_logger.error(f"Error handling peer {address[0]}:{address[1]}: {e}")
        finally:
            peer_socket.close()
            self.peers.discard(address)

    def _handle_message(self, message: Dict[str, Any], peer_socket: socket.socket) -> None:
        """
        Handle an incoming message from a peer.
        
        Args:
            message: Received message dictionary
            peer_socket: Socket connected to the sender
        """
        try:
            if message['type'] == 'handshake':
                # Add peer to list
                peer_host = message["host"]
                peer_port = message["port"]
                self.peers.add((peer_host, peer_port))
                
            elif message['type'] == 'get_blockchain':
                # Send current blockchain state
                self._send_message(peer_socket, {
                    "type": "blockchain",
                    "data": self.blockchain.to_dict()
                })
                
            elif message['type'] == 'transaction':
                tx_data = deserialize_transaction(message['data'])
                # Verify transaction signature
                if not verify_signature(tx_data['from'], serialize_transaction(tx_data), tx_data['signature']):
                    networking_logger.error("Invalid transaction signature")
                    return
                    
                if is_valid_transaction(tx_data):
                    # Add transaction to pool
                    if self.blockchain.add_transaction(tx_data):
                        # Forward to other peers
                        self._broadcast_to_peers(message, exclude=peer_socket)
                    
            elif message['type'] == 'block':
                block = message['data']
                # Verify block signature
                if not verify_signature(block['validator'], block['hash'], block['signature']):
                    networking_logger.error("Invalid block signature")
                    return
                    
                if is_valid_block(block, self.blockchain.get_latest_block()):
                    # Add block to chain
                    if self.blockchain.add_block(block):
                        # Forward to other peers
                        self._broadcast_to_peers(message, exclude=peer_socket)
                    
            elif message['type'] == 'blockchain':
                # Compare received chain with current chain
                received_chain = Blockchain.from_dict(message["data"])
                if len(received_chain.chain) > len(self.blockchain.chain):
                    if received_chain.is_valid_chain():
                        self.blockchain = received_chain
                        
            elif message['type'] == 'new_peer':
                # Connect to new peer
                peer_host = message["host"]
                peer_port = message["port"]
                if (peer_host, peer_port) != (self.host, self.port):
                    self.connect_to_peer(peer_host, peer_port)

        except Exception as e:
            networking_logger.error(f"Error handling message: {e}")

    def _broadcast_to_peers(self, message: Dict[str, Any], exclude: Optional[socket.socket] = None) -> None:
        """
        Broadcast a message to all peers.
        
        Args:
            message: Message to broadcast
            exclude: Socket to exclude from broadcast
        """
        for peer in self.peers.copy():
            try:
                if peer != exclude:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect(peer)
                        self._send_message(sock, message)
            except Exception as e:
                networking_logger.error(f"Failed to broadcast to {peer[0]}:{peer[1]}: {e}")
                self.peers.discard(peer)

    @staticmethod
    def _send_message(sock: socket.socket, message: Dict[str, Any]) -> None:
        """
        Send a message over a socket.
        
        Args:
            sock: Socket to send message over
            message: Message to send
        """
        try:
            data = json.dumps(message).encode()
            length = len(data).to_bytes(4, byteorder='big')
            sock.sendall(length + data)
        except Exception as e:
            networking_logger.error(f"Error sending message: {e}")
            raise

    @staticmethod
    def _receive_message(sock: socket.socket) -> Optional[Dict[str, Any]]:
        """
        Receive a message from a socket.
        
        Args:
            sock: Socket to receive message from
            
        Returns:
            Dict containing the received message, or None if connection closed
        """
        try:
            # Read message length
            if not (length_bytes := sock.recv(4)):
                return None
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Read message data
            message_bytes = b''
            while len(message_bytes) < message_length:
                if not (chunk := sock.recv(min(message_length - len(message_bytes), 4096))):
                    return None
                message_bytes += chunk
            
            return json.loads(message_bytes.decode())
        except Exception as e:
            networking_logger.error(f"Error receiving message: {e}")
            raise 