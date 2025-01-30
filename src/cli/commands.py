"""
Core CLI commands for Vernachain
"""

from ..networking.bootstrap_node import BootstrapNode
from ..networking.node import Node

def start_bootstrap(host: str = 'localhost', port: int = 5000, log_level: str = 'info'):
    """Start a bootstrap node"""
    node = BootstrapNode(host=host, port=port)
    try:
        print(f"Starting bootstrap node on {host}:{port}")
        node.start()
    except KeyboardInterrupt:
        print("\nShutting down bootstrap node...")
        node.running = False

def start_node(host: str = 'localhost', port: int = 5001, 
               bootstrap_host: str = None, bootstrap_port: int = None,
               log_level: str = 'info'):
    """Start a regular node"""
    node = Node(
        host=host,
        port=port,
        bootstrap_host=bootstrap_host,
        bootstrap_port=bootstrap_port
    )
    try:
        print(f"Starting node on {host}:{port}")
        if bootstrap_host and bootstrap_port:
            print(f"Connecting to bootstrap node at {bootstrap_host}:{bootstrap_port}")
        node.start()
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.running = False 