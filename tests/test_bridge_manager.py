"""Tests for the Cross-Chain Bridge Manager."""

import pytest
from datetime import datetime, timedelta
from src.bridge.bridge_manager import (
    BridgeManager, ChainConfig, ChainType, BridgeStatus
)

@pytest.fixture
def bridge_manager():
    """Create a bridge manager instance for testing."""
    return BridgeManager(min_validators=2)

@pytest.fixture
def eth_config():
    """Create Ethereum chain configuration."""
    return ChainConfig(
        chain_type=ChainType.ETHEREUM,
        chain_id=1,
        rpc_endpoint="https://eth-mainnet.example.com",
        required_confirmations=12,
        gas_limit=300000,
        bridge_contract_address="0x1234567890123456789012345678901234567890",
        token_contracts={"USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7"}
    )

@pytest.fixture
def verna_config():
    """Create Vernachain configuration."""
    return ChainConfig(
        chain_type=ChainType.VERNACHAIN,
        chain_id=1337,
        rpc_endpoint="http://localhost:8545",
        required_confirmations=6,
        gas_limit=500000,
        bridge_contract_address="0x0987654321098765432109876543210987654321",
        token_contracts={"USDT": "0x0987654321098765432109876543210987654321"}
    )

@pytest.fixture
def validator_addresses():
    """Create test validator addresses."""
    return [
        "0x1111111111111111111111111111111111111111",
        "0x2222222222222222222222222222222222222222",
        "0x3333333333333333333333333333333333333333"
    ]

def test_chain_registration(bridge_manager, eth_config, verna_config):
    """Test chain registration process."""
    # Test successful registration
    assert bridge_manager.register_chain(eth_config)
    assert ChainType.ETHEREUM in bridge_manager.chains
    
    # Test duplicate registration
    assert not bridge_manager.register_chain(eth_config)
    
    # Test multiple chain registration
    assert bridge_manager.register_chain(verna_config)
    assert len(bridge_manager.chains) == 2

def test_validator_registration(bridge_manager, validator_addresses):
    """Test bridge validator registration."""
    # Test successful registration
    for addr in validator_addresses:
        assert bridge_manager.add_bridge_validator(addr)
    assert len(bridge_manager.bridge_validators) == len(validator_addresses)
    
    # Test duplicate registration
    assert not bridge_manager.add_bridge_validator(validator_addresses[0])

def test_transfer_initiation(bridge_manager, eth_config, verna_config):
    """Test cross-chain transfer initiation."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Test successful transfer initiation
    tx_hash = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    assert tx_hash is not None
    assert tx_hash in bridge_manager.transactions
    
    # Test transfer with inactive chain
    bridge_manager.chains[ChainType.ETHEREUM].is_active = False
    assert bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    ) is None
    
    # Test transfer exceeding limits
    bridge_manager.chains[ChainType.ETHEREUM].is_active = True
    assert bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=2000000.0
    ) is None

def test_transfer_validation(bridge_manager, eth_config, verna_config, validator_addresses):
    """Test transfer validation process."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Register validators
    for addr in validator_addresses[:2]:
        bridge_manager.add_bridge_validator(addr)
    
    # Initiate transfer
    tx_hash = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    
    # Test successful validation
    assert bridge_manager.validate_transfer(
        tx_hash,
        validator_addresses[0],
        b"signature1"
    )
    
    # Test duplicate validation
    assert not bridge_manager.validate_transfer(
        tx_hash,
        validator_addresses[0],
        b"signature1"
    )
    
    # Test validation by non-validator
    assert not bridge_manager.validate_transfer(
        tx_hash,
        "0x9999",
        b"signature3"
    )
    
    # Test validation with enough signatures
    assert bridge_manager.validate_transfer(
        tx_hash,
        validator_addresses[1],
        b"signature2"
    )
    assert bridge_manager.transactions[tx_hash].status == BridgeStatus.PROCESSING

def test_transfer_completion(bridge_manager, eth_config, verna_config, validator_addresses):
    """Test transfer completion process."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Register validators and initiate transfer
    for addr in validator_addresses[:2]:
        bridge_manager.add_bridge_validator(addr)
    
    tx_hash = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    
    # Validate transfer
    for addr in validator_addresses[:2]:
        bridge_manager.validate_transfer(tx_hash, addr, f"sig_{addr}".encode())
    
    # Test successful completion
    target_tx = "0x" + "9" * 64
    assert bridge_manager.complete_transfer(tx_hash, target_tx)
    assert bridge_manager.transactions[tx_hash].status == BridgeStatus.COMPLETED
    assert bridge_manager.transactions[tx_hash].target_tx_hash == target_tx
    
    # Test completion of non-existent transaction
    assert not bridge_manager.complete_transfer("invalid_hash", target_tx)
    
    # Test completion of already completed transaction
    assert not bridge_manager.complete_transfer(tx_hash, "0x" + "8" * 64)

def test_transfer_reversion(bridge_manager, eth_config, verna_config):
    """Test transfer reversion process."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Initiate transfer
    tx_hash = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    
    initial_locked = bridge_manager.locked_assets.get("USDT", 0.0)
    
    # Test successful reversion
    assert bridge_manager.revert_transfer(tx_hash, "Test reversion")
    assert bridge_manager.transactions[tx_hash].status == BridgeStatus.REVERTED
    assert bridge_manager.locked_assets.get("USDT", 0.0) < initial_locked
    
    # Test reversion of completed transaction
    tx_hash2 = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    bridge_manager.transactions[tx_hash2].status = BridgeStatus.COMPLETED
    assert not bridge_manager.revert_transfer(tx_hash2, "Test reversion")

def test_fee_calculation(bridge_manager, eth_config, verna_config):
    """Test bridge fee calculation."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    amount = 1000.0
    
    # Test Ethereum to Vernachain fee (higher due to Ethereum)
    eth_fee = bridge_manager._calculate_fee(
        ChainType.ETHEREUM,
        ChainType.VERNACHAIN,
        amount
    )
    
    # Test Vernachain to Vernachain fee (lower for internal transfers)
    verna_fee = bridge_manager._calculate_fee(
        ChainType.VERNACHAIN,
        ChainType.VERNACHAIN,
        amount
    )
    
    assert eth_fee > verna_fee

def test_volume_limits(bridge_manager, eth_config, verna_config):
    """Test daily volume limits."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Test successful volume update
    assert bridge_manager._check_and_update_volume("USDT", 1000000.0)
    
    # Test volume limit exceeded
    assert not bridge_manager._check_and_update_volume("USDT", 5000000.0)
    
    # Test volume reset after a day
    bridge_manager.last_volume_reset = datetime.now() - timedelta(days=1, minutes=1)
    assert bridge_manager._check_and_update_volume("USDT", 1000000.0)

def test_bridge_stats(bridge_manager, eth_config, verna_config, validator_addresses):
    """Test bridge statistics retrieval."""
    bridge_manager.register_chain(eth_config)
    bridge_manager.register_chain(verna_config)
    
    # Register validators
    for addr in validator_addresses:
        bridge_manager.add_bridge_validator(addr)
    
    # Create some transactions
    tx_hash1 = bridge_manager.initiate_transfer(
        from_chain=ChainType.ETHEREUM,
        to_chain=ChainType.VERNACHAIN,
        from_address="0x1234",
        to_address="0x5678",
        token="USDT",
        amount=1000.0
    )
    
    tx_hash2 = bridge_manager.initiate_transfer(
        from_chain=ChainType.VERNACHAIN,
        to_chain=ChainType.ETHEREUM,
        from_address="0x5678",
        to_address="0x1234",
        token="USDT",
        amount=2000.0
    )
    
    # Validate and complete one transaction
    bridge_manager.validate_transfer(tx_hash1, validator_addresses[0], b"sig1")
    bridge_manager.validate_transfer(tx_hash1, validator_addresses[1], b"sig2")
    
    # Get stats
    stats = bridge_manager.get_bridge_stats()
    
    assert len(stats['active_chains']) == 2
    assert stats['validator_count'] == len(validator_addresses)
    assert stats['pending_transactions'] == 1
    assert stats['processing_transactions'] == 1
    assert "USDT" in stats['locked_assets']
    assert "USDT" in stats['daily_volumes'] 