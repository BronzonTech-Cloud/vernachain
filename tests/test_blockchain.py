"""Tests for Vernachain blockchain operations."""

import pytest
from datetime import datetime, timedelta
from src.blockchain.blockchain import Blockchain
from src.blockchain.transaction import Transaction
from src.utils.crypto import generate_key_pair, sign_message

@pytest.fixture
def blockchain():
    """Create a blockchain instance for testing."""
    return Blockchain()

@pytest.fixture
def validator_keys():
    """Generate validator keys for testing."""
    return generate_key_pair()

def test_genesis_block(blockchain):
    """Test genesis block creation."""
    genesis = blockchain.get_latest_block()
    
    assert genesis['index'] == 0
    assert genesis['previous_hash'] == '0' * 64
    assert len(genesis['transactions']) == 0
    assert genesis['validator'] is None

def test_add_transaction(blockchain):
    """Test adding transactions to the blockchain."""
    # Create transaction
    tx = {
        'from': "0x1234567890abcdef1234567890abcdef12345678",
        'to': "0xabcdef1234567890abcdef1234567890abcdef12",
        'value': 100.0,
        'nonce': 1,
        'timestamp': datetime.now(),
        'signature': b'signature'
    }
    
    # Add transaction
    success = blockchain.add_transaction(tx)
    assert success
    assert len(blockchain.pending_transactions) == 1
    
    # Test invalid transaction
    invalid_tx = tx.copy()
    invalid_tx['value'] = -100
    assert not blockchain.add_transaction(invalid_tx)

def test_create_block(blockchain, validator_keys):
    """Test block creation."""
    private_key, public_key = validator_keys
    
    # Add validator
    blockchain.add_validator(public_key, 1000)
    
    # Add some transactions
    for i in range(3):
        tx = {
            'from': "0x1234567890abcdef1234567890abcdef12345678",
            'to': "0xabcdef1234567890abcdef1234567890abcdef12",
            'value': 100.0,
            'nonce': i,
            'timestamp': datetime.now(),
            'signature': b'signature'
        }
        blockchain.add_transaction(tx)
    
    # Create block
    block = blockchain.create_block(public_key)
    assert block is not None
    assert block['index'] == 1
    assert len(block['transactions']) == 3
    assert block['validator'] == public_key

def test_add_block(blockchain, validator_keys):
    """Test adding blocks to the blockchain."""
    private_key, public_key = validator_keys
    
    # Add validator
    blockchain.add_validator(public_key, 1000)
    
    # Create and add block
    block = blockchain.create_block(public_key)
    signature = sign_message(private_key, block['hash'])
    
    success = blockchain.add_block(block, signature)
    assert success
    assert len(blockchain.chain) == 2
    assert blockchain.get_latest_block()['hash'] == block['hash']

def test_validator_operations(blockchain):
    """Test validator management."""
    # Add validator
    address = "0x1234567890abcdef1234567890abcdef12345678"
    success = blockchain.add_validator(address, 2000)
    assert success
    assert address in blockchain.validators
    assert blockchain.validators[address] == 2000
    
    # Remove validator
    success = blockchain.remove_validator(address)
    assert success
    assert address not in blockchain.validators

def test_get_balance(blockchain):
    """Test balance calculation."""
    address = "0x1234567890abcdef1234567890abcdef12345678"
    
    # Add transactions
    tx1 = {
        'from': "0xabcdef1234567890abcdef1234567890abcdef12",
        'to': address,
        'value': 100.0,
        'nonce': 1,
        'timestamp': datetime.now(),
        'signature': b'signature'
    }
    tx2 = {
        'from': address,
        'to': "0xabcdef1234567890abcdef1234567890abcdef12",
        'value': 30.0,
        'nonce': 2,
        'timestamp': datetime.now(),
        'signature': b'signature'
    }
    
    # Create block with transactions
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    validator = "0x9876543210fedcba9876543210fedcba98765432"
    blockchain.add_validator(validator, 1000)
    
    block = blockchain.create_block(validator)
    blockchain.add_block(block, b'signature')
    
    # Check balance
    balance = blockchain.get_balance(address)
    assert balance == 70.0  # 100 received - 30 sent

def test_blockchain_validation(blockchain, validator_keys):
    """Test blockchain validation."""
    private_key, public_key = validator_keys
    blockchain.add_validator(public_key, 1000)
    
    # Add some blocks
    for i in range(3):
        block = blockchain.create_block(public_key)
        signature = sign_message(private_key, block['hash'])
        blockchain.add_block(block, signature)
    
    # Validate chain
    assert blockchain.is_valid_chain()
    
    # Test invalid chain
    blockchain.chain[1]['hash'] = 'invalid_hash'
    assert not blockchain.is_valid_chain()

def test_fork_resolution(blockchain, validator_keys):
    """Test blockchain fork resolution."""
    private_key, public_key = validator_keys
    blockchain.add_validator(public_key, 1000)
    
    # Create fork
    original_block = blockchain.create_block(public_key)
    fork_block = blockchain.create_block(public_key)
    
    # Add different transactions to fork
    fork_block['transactions'].append({
        'from': "0x1234567890abcdef1234567890abcdef12345678",
        'to': "0xabcdef1234567890abcdef1234567890abcdef12",
        'value': 50.0,
        'nonce': 1,
        'timestamp': datetime.now(),
        'signature': b'signature'
    })
    
    # Sign and add blocks
    signature1 = sign_message(private_key, original_block['hash'])
    signature2 = sign_message(private_key, fork_block['hash'])
    
    blockchain.add_block(original_block, signature1)
    assert not blockchain.add_block(fork_block, signature2)  # Should reject fork 