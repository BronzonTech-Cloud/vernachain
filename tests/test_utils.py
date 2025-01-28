"""Tests for Vernachain utility functions."""

import pytest
from datetime import datetime
from src.utils.validation import (
    is_valid_address,
    is_valid_transaction,
    is_valid_block,
    is_valid_stake_amount,
    is_valid_contract_code
)
from src.utils.serialization import (
    serialize_transaction,
    deserialize_transaction,
    serialize_block,
    deserialize_block
)

# Test Validation Functions
def test_valid_address():
    """Test address validation."""
    # Valid addresses
    assert is_valid_address("0x1234567890abcdef1234567890abcdef12345678")
    assert is_valid_address("0xABCDEF1234567890abcdef1234567890abcdef12")
    
    # Invalid addresses
    assert not is_valid_address("0x123")  # Too short
    assert not is_valid_address("0xGHIJKL1234567890abcdef1234567890abcdef12")  # Invalid chars
    assert not is_valid_address("1234567890abcdef1234567890abcdef12345678")  # Missing 0x
    assert not is_valid_address("")  # Empty string

def test_valid_transaction():
    """Test transaction validation."""
    valid_tx = {
        'from': "0x1234567890abcdef1234567890abcdef12345678",
        'to': "0xabcdef1234567890abcdef1234567890abcdef12",
        'value': 100.0,
        'nonce': 1,
        'signature': b'signature'
    }
    assert is_valid_transaction(valid_tx)
    
    # Test invalid transactions
    invalid_tx_missing_field = valid_tx.copy()
    del invalid_tx_missing_field['signature']
    assert not is_valid_transaction(invalid_tx_missing_field)
    
    invalid_tx_negative_value = valid_tx.copy()
    invalid_tx_negative_value['value'] = -100
    assert not is_valid_transaction(invalid_tx_negative_value)
    
    invalid_tx_negative_nonce = valid_tx.copy()
    invalid_tx_negative_nonce['nonce'] = -1
    assert not is_valid_transaction(invalid_tx_negative_nonce)
    
    invalid_tx_invalid_address = valid_tx.copy()
    invalid_tx_invalid_address['from'] = "invalid_address"
    assert not is_valid_transaction(invalid_tx_invalid_address)

def test_valid_block():
    """Test block validation."""
    valid_block = {
        'index': 1,
        'timestamp': datetime.now(),
        'transactions': [],
        'previous_hash': "0" * 64,
        'validator': "0x1234567890abcdef1234567890abcdef12345678",
        'hash': "1" * 64
    }
    
    previous_block = {
        'index': 0,
        'timestamp': datetime(2024, 1, 1),
        'transactions': [],
        'previous_hash': "0" * 64,
        'validator': None,
        'hash': "0" * 64
    }
    
    assert is_valid_block(valid_block, previous_block)
    
    # Test invalid blocks
    invalid_block_wrong_index = valid_block.copy()
    invalid_block_wrong_index['index'] = 2
    assert not is_valid_block(invalid_block_wrong_index, previous_block)
    
    invalid_block_wrong_timestamp = valid_block.copy()
    invalid_block_wrong_timestamp['timestamp'] = datetime(2023, 1, 1)
    assert not is_valid_block(invalid_block_wrong_timestamp, previous_block)

def test_valid_stake_amount():
    """Test stake amount validation."""
    assert is_valid_stake_amount(1000)  # Minimum stake
    assert is_valid_stake_amount(2000)  # Above minimum
    
    assert not is_valid_stake_amount(999)  # Below minimum
    assert not is_valid_stake_amount(0)    # Zero stake
    assert not is_valid_stake_amount(-100)  # Negative stake

def test_valid_contract_code():
    """Test contract code validation."""
    valid_code = """
    def transfer(to_address: str, amount: float):
        if amount > 0:
            return True
        return False
    """
    assert is_valid_contract_code(valid_code)
    
    # Test invalid contract code
    invalid_code_os = "import os\ndef hack(): pass"
    assert not is_valid_contract_code(invalid_code_os)
    
    invalid_code_eval = "eval('print(1)')"
    assert not is_valid_contract_code(invalid_code_eval)
    
    invalid_code_file = "open('secrets.txt', 'r').read()"
    assert not is_valid_contract_code(invalid_code_file)

# Test Serialization Functions
def test_transaction_serialization():
    """Test transaction serialization/deserialization."""
    tx = {
        'from': "0x1234567890abcdef1234567890abcdef12345678",
        'to': "0xabcdef1234567890abcdef1234567890abcdef12",
        'value': 100.0,
        'nonce': 1,
        'timestamp': datetime.now(),
        'signature': b'signature'
    }
    
    # Test serialization
    serialized = serialize_transaction(tx)
    assert isinstance(serialized, str)
    
    # Test deserialization
    deserialized = deserialize_transaction(serialized)
    assert isinstance(deserialized['timestamp'], datetime)
    assert isinstance(deserialized['signature'], bytes)
    assert deserialized['value'] == tx['value']
    assert deserialized['nonce'] == tx['nonce']

def test_block_serialization():
    """Test block serialization/deserialization."""
    block = {
        'index': 1,
        'timestamp': datetime.now(),
        'transactions': [
            {
                'from': "0x1234567890abcdef1234567890abcdef12345678",
                'to': "0xabcdef1234567890abcdef1234567890abcdef12",
                'value': 100.0,
                'nonce': 1,
                'timestamp': datetime.now(),
                'signature': b'signature'
            }
        ],
        'previous_hash': "0" * 64,
        'validator': "0x1234567890abcdef1234567890abcdef12345678",
        'hash': "1" * 64
    }
    
    # Test serialization
    serialized = serialize_block(block)
    assert isinstance(serialized, str)
    
    # Test deserialization
    deserialized = deserialize_block(serialized)
    assert isinstance(deserialized['timestamp'], datetime)
    assert isinstance(deserialized['transactions'][0]['timestamp'], datetime)
    assert isinstance(deserialized['transactions'][0]['signature'], bytes)
    assert deserialized['index'] == block['index']
    assert deserialized['previous_hash'] == block['previous_hash'] 