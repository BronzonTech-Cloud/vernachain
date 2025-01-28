"""Tests for Vernachain cryptographic functions."""

import pytest
from src.utils.crypto import (
    generate_key_pair,
    sign_message,
    verify_signature,
    hash_data,
    generate_merkle_root
)

def test_key_pair_generation():
    """Test key pair generation."""
    private_key, public_key = generate_key_pair()
    
    # Check key formats
    assert isinstance(private_key, str)
    assert isinstance(public_key, str)
    assert private_key.startswith('-----BEGIN RSA PRIVATE KEY-----')
    assert public_key.startswith('-----BEGIN PUBLIC KEY-----')

def test_message_signing():
    """Test message signing and verification."""
    # Generate keys
    private_key, public_key = generate_key_pair()
    
    # Sign message
    message = "Test message"
    signature = sign_message(private_key, message)
    
    # Verify signature
    assert verify_signature(public_key, message, signature)
    
    # Test invalid signature
    invalid_message = "Wrong message"
    assert not verify_signature(public_key, invalid_message, signature)
    
    # Test invalid signature bytes
    invalid_signature = b'invalid_signature'
    assert not verify_signature(public_key, message, invalid_signature)

def test_hash_data():
    """Test data hashing."""
    # Test basic hashing
    data = "test data"
    hash1 = hash_data(data)
    hash2 = hash_data(data)
    
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 produces 32 bytes = 64 hex chars
    assert hash1 == hash2  # Same data should produce same hash
    
    # Test different data produces different hashes
    other_data = "other data"
    other_hash = hash_data(other_data)
    assert hash1 != other_hash

def test_merkle_root():
    """Test Merkle root generation."""
    # Test with even number of items
    transactions = ["tx1", "tx2", "tx3", "tx4"]
    tx_hashes = [hash_data(tx) for tx in transactions]
    root = generate_merkle_root(tx_hashes)
    
    assert isinstance(root, str)
    assert len(root) == 64
    
    # Test with odd number of items
    transactions = ["tx1", "tx2", "tx3"]
    tx_hashes = [hash_data(tx) for tx in transactions]
    root = generate_merkle_root(tx_hashes)
    
    assert isinstance(root, str)
    assert len(root) == 64
    
    # Test empty list
    assert generate_merkle_root([]) == ""
    
    # Test single item
    single_hash = hash_data("tx1")
    assert generate_merkle_root([single_hash]) == single_hash

def test_signature_verification_edge_cases():
    """Test signature verification edge cases."""
    private_key, public_key = generate_key_pair()
    message = "Test message"
    
    # Test empty message
    empty_signature = sign_message(private_key, "")
    assert verify_signature(public_key, "", empty_signature)
    
    # Test long message
    long_message = "x" * 1000
    long_signature = sign_message(private_key, long_message)
    assert verify_signature(public_key, long_message, long_signature)
    
    # Test special characters
    special_message = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    special_signature = sign_message(private_key, special_message)
    assert verify_signature(public_key, special_message, special_signature)

def test_merkle_root_properties():
    """Test Merkle root mathematical properties."""
    tx1, tx2, tx3, tx4 = "tx1", "tx2", "tx3", "tx4"
    h1, h2, h3, h4 = [hash_data(tx) for tx in (tx1, tx2, tx3, tx4)]
    
    # Test commutativity of pairs
    root1 = generate_merkle_root([h1, h2, h3, h4])
    root2 = generate_merkle_root([h2, h1, h4, h3])
    assert root1 == root2
    
    # Test different ordering produces different roots
    root3 = generate_merkle_root([h1, h3, h2, h4])
    assert root1 != root3  # Order matters between different pairs 