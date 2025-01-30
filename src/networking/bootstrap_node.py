import json
import socket
import threading
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass, field
from src.utils.logging import get_networking_logger

logger = get_networking_logger()

@dataclass
class BootstrapNode:
    host: str = 'localhost'
    port: int = 5000
    peers: Set[tuple] = field(default_factory=set)
    running: bool = False
    
    def __post_init__(self):
        """Initialize additional attributes after dataclass initialization."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Enable address reuse to prevent "Address already in use" errors
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info("Bootstrap node initialized")

    def start(self) -> None:
        """Start the bootstrap node server."""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"Bootstrap node started on {self.host}:{self.port}")
            
            # Start listening for connections
            while self.running:
                try:
                    client_sock, address = self.socket.accept()
                    logger.info(f"New connection from {address[0]}:{address[1]}")
                    
                    # Handle client in a new thread
                    handler_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, address)
                    )
                    handler_thread.daemon = True
                    handler_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start bootstrap node: {e}")
            self.running = False
        finally:
            if self.socket:
                self.socket.close()
                logger.info("Bootstrap node stopped")

    def stop(self) -> None:
        """Stop the bootstrap node server."""
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("Bootstrap node stopped")

    def _handle_client(self, client_sock: socket.socket, address: tuple) -> None:
        """
        Handle client connections and requests.
        
        Args:
            client_sock: Socket connected to client
            address: Client's address tuple (host, port)
        """
        try:
            while self.running:
                if message := self._receive_message(client_sock):
                    match message.get("type"):
                        case "register":
                            # Register new peer
                            peer_host = message["host"]
                            peer_port = message["port"]
                            self.peers.add((peer_host, peer_port))
                            logger.info(f"New peer registered: {peer_host}:{peer_port}")
                            
                            # Send list of known peers
                            response = {
                                "type": "peers",
                                "peers": list(self.peers)
                            }
                            self._send_message(client_sock, response)
                            logger.debug(f"Sent peer list to {peer_host}:{peer_port}")
                            
                            # Broadcast new peer to existing peers
                            self._broadcast_new_peer(peer_host, peer_port)
                            
                        case "get_peers":
                            # Send list of known peers
                            response = {
                                "type": "peers",
                                "peers": list(self.peers)
                            }
                            self._send_message(client_sock, response)
                            logger.debug(f"Sent peer list to {address[0]}:{address[1]}")
                else:
                    break
                    
        except Exception as e:
            logger.error(f"Error handling client {address[0]}:{address[1]}: {e}")
        finally:
            client_sock.close()
            logger.debug(f"Closed connection to {address[0]}:{address[1]}")

    def _broadcast_new_peer(self, peer_host: str, peer_port: int) -> None:
        """
        Broadcast new peer to all existing peers.
        
        Args:
            peer_host: New peer's host address
            peer_port: New peer's port
        """
        message = {
            "type": "new_peer",
            "host": peer_host,
            "port": peer_port
        }
        
        logger.info(f"Broadcasting new peer {peer_host}:{peer_port} to network")
        
        # Send to all peers except the new one
        for peer in self.peers.copy():
            if peer != (peer_host, peer_port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect(peer)
                        self._send_message(sock, message)
                        logger.debug(f"Broadcast sent to {peer[0]}:{peer[1]}")
                except Exception as e:
                    logger.error(f"Failed to broadcast to {peer[0]}:{peer[1]}: {e}")
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
            message_bytes = json.dumps(message).encode()
            message_length = len(message_bytes).to_bytes(4, byteorder='big')
            sock.sendall(message_length + message_bytes)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
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
            logger.error(f"Error receiving message: {e}")
            raise 