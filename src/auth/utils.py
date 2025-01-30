"""Utility functions for authentication and security."""

import secrets
import hashlib
import hmac
import base64
import json
from typing import Dict, Optional, Tuple, List
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from eth_account import Account
from eth_account.messages import encode_defunct
from web3.types import ChecksumAddress
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utility class for security operations."""
    
    def __init__(self, master_key: str):
        """Initialize security utils."""
        self.master_key = master_key.encode()
        self._setup_encryption()
    
    def _setup_encryption(self) -> None:
        """Set up encryption keys."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"static_salt",  # In production, use a proper salt management
            iterations=100000,
        )
        self.derived_key = kdf.derive(self.master_key)
        self.fernet = Fernet(base64.urlsafe_b64encode(self.derived_key))
    
    def generate_token(self, data: Dict, expiry: int = 3600) -> str:
        """Generate JWT token with enhanced security."""
        now = datetime.utcnow()
        payload = {
            **data,
            "iat": now,
            "exp": now + timedelta(seconds=expiry),
            "jti": secrets.token_hex(16)
        }
        return jwt.encode(payload, self.master_key, algorithm="HS512")
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Verify JWT token with enhanced security."""
        try:
            payload = jwt.decode(token, self.master_key, algorithms=["HS512"])
            return True, payload
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return False, None
    
    def encrypt_private_key(self, private_key: str, password: str) -> Dict:
        """Encrypt private key with password."""
        # Generate a random salt
        salt = secrets.token_bytes(16)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        
        # Generate nonce
        nonce = secrets.token_bytes(12)
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Encrypt private key
        ciphertext = aesgcm.encrypt(
            nonce,
            private_key.encode(),
            None  # Additional data
        )
        
        return {
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode()
        }
    
    def decrypt_private_key(self, encrypted_data: Dict, password: str) -> Optional[str]:
        """Decrypt private key with password."""
        try:
            # Decode components
            salt = base64.b64decode(encrypted_data["salt"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            
            # Create AESGCM cipher
            aesgcm = AESGCM(key)
            
            # Decrypt private key
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode()
            
        except Exception as e:
            logger.error(f"Private key decryption failed: {str(e)}")
            return None
    
    def generate_wallet(self, password: str) -> Tuple[ChecksumAddress, Dict]:
        """Generate new wallet with encrypted private key."""
        account = Account.create()
        encrypted_key = self.encrypt_private_key(
            account.key.hex(),
            password
        )
        return account.address, encrypted_key
    
    def sign_message(
        self,
        message: str,
        private_key: str,
        include_prefix: bool = True
    ) -> str:
        """Sign message with private key."""
        if include_prefix:
            message_hash = encode_defunct(text=message)
        else:
            message_hash = encode_defunct(hexstr=message)
        
        signed_message = Account.sign_message(
            message_hash,
            private_key=private_key
        )
        return signed_message.signature.hex()
    
    def verify_signature(
        self,
        message: str,
        signature: str,
        expected_address: ChecksumAddress,
        include_prefix: bool = True
    ) -> bool:
        """Verify message signature."""
        try:
            if include_prefix:
                message_hash = encode_defunct(text=message)
            else:
                message_hash = encode_defunct(hexstr=message)
            
            address = Account.recover_message(message_hash, signature=signature)
            return address.lower() == expected_address.lower()
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False
    
    def generate_session_id(self) -> str:
        """Generate secure session ID."""
        return secrets.token_urlsafe(32)
    
    def generate_api_key(self) -> Tuple[str, str]:
        """Generate API key and secret."""
        api_key = f"vk_{secrets.token_urlsafe(16)}"
        api_secret = secrets.token_urlsafe(32)
        return api_key, api_secret
    
    def verify_api_signature(
        self,
        api_key: str,
        api_secret: str,
        timestamp: str,
        payload: str,
        signature: str
    ) -> bool:
        """Verify API request signature."""
        try:
            message = f"{api_key}{timestamp}{payload}"
            expected_signature = hmac.new(
                api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"API signature verification failed: {str(e)}")
            return False
    
    def generate_backup_codes(self, count: int = 8) -> List[str]:
        """Generate backup recovery codes."""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup recovery codes for storage."""
        return [
            hashlib.sha256(code.encode()).hexdigest()
            for code in codes
        ]
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> bool:
        """Verify backup recovery code."""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return code_hash in hashed_codes
    
    def generate_device_fingerprint(
        self,
        user_agent: str,
        ip_address: str,
        additional_data: Optional[Dict] = None
    ) -> str:
        """Generate device fingerprint."""
        data = {
            "user_agent": user_agent,
            "ip_address": ip_address,
            **(additional_data or {})
        }
        fingerprint_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def encrypt_sensitive_data(self, data: Dict) -> str:
        """Encrypt sensitive data."""
        return self.fernet.encrypt(json.dumps(data).encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[Dict]:
        """Decrypt sensitive data."""
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Data decryption failed: {str(e)}")
            return None

def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        str: Generated token
    """
    return secrets.token_urlsafe(length)


def verify_token(token: str, secret_key: str, purpose: str) -> Optional[dict]:
    """
    Verify JWT token.
    
    Args:
        token: JWT token
        secret_key: Secret key for verification
        purpose: Expected token purpose
        
    Returns:
        Optional[dict]: Token payload if valid
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        if payload.get('purpose') != purpose:
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


def hash_password(password: str) -> str:
    """
    Create a secure hash of a password.
    
    Args:
        password: Password to hash
        
    Returns:
        str: Password hash
    """
    salt = secrets.token_bytes(16)
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000  # Number of iterations
    )
    return base64.b64encode(salt + hash_obj).decode()


def verify_password_hash(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Password to verify
        password_hash: Stored password hash
        
    Returns:
        bool: True if password matches
    """
    try:
        decoded = base64.b64decode(password_hash.encode())
        salt = decoded[:16]
        stored_hash = decoded[16:]
        
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000  # Number of iterations
        )
        
        return secrets.compare_digest(hash_obj, stored_hash)
    except Exception:
        return False


def generate_api_key() -> str:
    """
    Generate an API key.
    
    Returns:
        str: Generated API key
    """
    # Format: verna_live_xxxxxxxxxx or verna_test_xxxxxxxxxx
    prefix = 'verna_live_' if not secrets.randbelow(2) else 'verna_test_'
    random_part = secrets.token_urlsafe(24)
    return f"{prefix}{random_part}"


def create_session_token(user_id: str, secret_key: str,
                        duration: timedelta = timedelta(hours=24)) -> str:
    """
    Create a session token.
    
    Args:
        user_id: User ID
        secret_key: Secret key for signing
        duration: Token duration
        
    Returns:
        str: JWT session token
    """
    payload = {
        'user_id': user_id,
        'purpose': 'session',
        'exp': datetime.utcnow() + duration,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256') 