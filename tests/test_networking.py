"""Tests for Vernachain networking components."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.networking.node import Node
from src.networking.bootstrap_node import BootstrapNode
from src.networking.manager import NetworkManager
from src.utils.serialization import serialize_transaction

@pytest.fixture
def bootstrap_node():
    """Create a bootstrap node for testing."""
    node = BootstrapNode(host='localhost', port=5000)
    yield node
    node.stop()

@pytest.fixture
def regular_node():
    """Create a regular node for testing."""
    node = Node(
        host='localhost',
        port=5001,
        bootstrap_host='localhost',
        bootstrap_port=5000
    )
    yield node
    node.stop()

@pytest.fixture
def network_manager():
    """Create a network manager for testing."""
    manager = NetworkManager(
        host='localhost',
        port=5002,
        bootstrap_nodes=[{'host': 'localhost', 'port': 5000}]
    )
    yield manager
    asyncio.run(manager.stop())

def test_bootstrap_node_initialization(bootstrap_node):
    """Test bootstrap node initialization."""
    assert bootstrap_node.host == 'localhost'
    assert bootstrap_node.port == 5000
    assert bootstrap_node.peers == set()
    assert not bootstrap_node.running

@pytest.mark.asyncio
async def test_node_connection(bootstrap_node, regular_node):
    """Test node connection to bootstrap node."""
    # Start bootstrap node
    bootstrap_node.start()
    
    # Connect regular node
    regular_node.start()
    
    # Wait for connection
    await asyncio.sleep(1)
    
    # Verify connection
    assert (regular_node.host, regular_node.port) in bootstrap_node.peers
    assert len(regular_node.peers) > 0

def test_peer_discovery(bootstrap_node):
    """Test peer discovery mechanism."""
    # Create multiple nodes
    nodes = [
        Node('localhost', 5001 + i, 'localhost', 5000)
        for i in range(3)
    ]
    
    # Start bootstrap node
    bootstrap_node.start()
    
    # Start and connect nodes
    for node in nodes:
        node.start()
    
    # Wait for peer discovery
    asyncio.run(asyncio.sleep(2))
    
    # Verify peer connections
    for node in nodes:
        assert len(node.peers) >= len(nodes) - 1
        
    # Cleanup
    for node in nodes:
        node.stop()

@pytest.mark.asyncio
async def test_message_broadcasting(network_manager):
    """Test message broadcasting."""
    # Start network manager
    await network_manager.start()
    
    # Create mock message handler
    message_received = asyncio.Event()
    
    async def message_handler(msg_type, payload):
        if msg_type == 'test':
            message_received.set()
    
    # Register message handler
    network_manager.register_message_handler('test', message_handler)
    
    # Broadcast message
    await network_manager.broadcast_message('test', {'data': 'test_data'})
    
    # Wait for message
    try:
        await asyncio.wait_for(message_received.wait(), timeout=2)
        assert message_received.is_set()
    except asyncio.TimeoutError:
        pytest.fail("Message not received in time")

@pytest.mark.asyncio
async def test_network_manager_maintenance(network_manager):
    """Test network manager maintenance tasks."""
    # Start network manager
    await network_manager.start()
    
    # Wait for maintenance cycle
    await asyncio.sleep(2)
    
    # Verify network state
    stats = network_manager.get_network_stats()
    assert isinstance(stats['connected_peers'], int)
    assert isinstance(stats['active_connections'], int)

@pytest.mark.asyncio
async def test_node_reconnection(network_manager):
    """Test node reconnection after disconnect."""
    # Start network manager
    await network_manager.start()
    
    # Simulate network disconnect
    await network_manager.stop()
    
    # Wait and reconnect
    await asyncio.sleep(1)
    await network_manager.start()
    
    # Verify reconnection
    await asyncio.sleep(1)
    stats = network_manager.get_network_stats()
    assert stats['connected_peers'] > 0

@pytest.mark.asyncio
async def test_message_validation(network_manager):
    """Test message validation during broadcasting."""
    await network_manager.start()
    
    # Test invalid message type
    with pytest.raises(ValueError):
        await network_manager.broadcast_message('', {'data': 'test'})
        
    # Test invalid payload
    with pytest.raises(ValueError):
        await network_manager.broadcast_message('test', None)

@pytest.mark.asyncio
async def test_peer_banning(network_manager):
    """Test peer banning mechanism."""
    await network_manager.start()
    
    # Ban a peer
    peer_address = ('localhost', 5003)
    network_manager.ban_peer(*peer_address)
    
    # Verify peer is banned
    assert peer_address in network_manager.banned_peers
    
    # Try to connect to banned peer
    success = await network_manager.protocol.connect(*peer_address)
    assert not success 