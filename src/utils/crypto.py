"""Cryptographic utility functions for Vernachain."""

from typing import Tuple
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def generate_key_pair() -> Tuple[str, str]:
    """Generate a new RSA key pair.
    
    Returns:
        Tuple[str, str]: (private_key, public_key) in PEM format
    """
    key = RSA.generate(2048)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key

def sign_message(private_key: str, message: str) -> bytes:
    """Sign a message using RSA private key.
    
    Args:
        private_key: Private key in PEM format
        message: Message to sign
        
    Returns:
        bytes: Digital signature
    """
    key = RSA.import_key(private_key)
    h = SHA256.new(message.encode())
    signature = pkcs1_15.new(key).sign(h)
    return signature

def verify_signature(public_key: str, message: str, signature: bytes) -> bool:
    """Verify a signature using RSA public key.
    
    Args:
        public_key: Public key in PEM format
        message: Original message
        signature: Signature to verify
        
    Returns:
        bool: True if signature is valid
    """
    try:
        key = RSA.import_key(public_key)
        h = SHA256.new(message.encode())
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

def hash_data(data: str) -> str:
    """Create SHA256 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        str: Hexadecimal hash string
    """
    return hashlib.sha256(data.encode()).hexdigest()

def generate_merkle_root(hashes: list) -> str:
    """Generate Merkle root from list of hashes.
    
    Args:
        hashes: List of hash strings
        
    Returns:
        str: Merkle root hash
    """
    if not hashes:
        return ""
    
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            next_level.append(hash_data(combined))
        hashes = next_level
        
    return hashes[0] 