"""
Wallet management service for handling user wallets.
"""

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import os
from typing import Dict, Any, Tuple, Optional
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import json
import uuid
import time
import hmac
import hashlib
import pyotp

logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        self.web3 = Web3()
        # Initialize encryption keys
        self.master_key = os.getenv("WALLET_MASTER_KEY", Fernet.generate_key())
        self.encryption_key = self._derive_key(self.master_key)
        self.fernet = Fernet(self.encryption_key)
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.failed_attempts = {}
        self.lockouts = {}
        
        # Transaction limits
        self.daily_limit = int(os.getenv("DAILY_TRANSFER_LIMIT", "1000000000000000000"))  # 1 ETH
        self.transaction_limits = {}

    def _derive_key(self, master_key: bytes, salt: bytes = None) -> bytes:
        """Derive encryption key from master key"""
        if not salt:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_key))

    def create_wallet(self, password: str) -> Tuple[str, str]:
        """Create a new wallet with password protection"""
        account = Account.create()
        salt = os.urandom(16)
        key = self._derive_key(password.encode(), salt)
        encrypted_key = self._encrypt_private_key(account.key.hex(), key)
        return account.address, json.dumps({
            "key": encrypted_key,
            "salt": base64.b64encode(salt).decode()
        })

    def _encrypt_private_key(self, private_key: str, key: bytes) -> str:
        """Encrypt private key with additional security"""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(
            nonce,
            private_key.encode(),
            None
        )
        return base64.b64encode(nonce + ciphertext).decode()

    def _decrypt_private_key(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt private key with additional security"""
        try:
            data = base64.b64decode(encrypted_data)
            nonce = data[:12]
            ciphertext = data[12:]
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(nonce, ciphertext, None).decode()
        except Exception as e:
            logger.error(f"Failed to decrypt private key: {e}")
            raise ValueError("Invalid encryption key or corrupted data")

    def verify_password(self, address: str, password: str) -> bool:
        """Verify wallet password with rate limiting"""
        if self._is_locked_out(address):
            raise ValueError("Account is temporarily locked")

        try:
            # Verify password (implementation depends on how passwords are stored)
            is_valid = self._check_password(address, password)
            if not is_valid:
                self._record_failed_attempt(address)
            else:
                self._reset_failed_attempts(address)
            return is_valid
        except Exception as e:
            self._record_failed_attempt(address)
            raise

    def _is_locked_out(self, address: str) -> bool:
        """Check if address is locked out"""
        if address in self.lockouts:
            if time.time() < self.lockouts[address]:
                return True
            del self.lockouts[address]
        return False

    def _record_failed_attempt(self, address: str):
        """Record failed login attempt"""
        current_time = time.time()
        if address not in self.failed_attempts:
            self.failed_attempts[address] = []
        
        # Remove old attempts
        self.failed_attempts[address] = [
            t for t in self.failed_attempts[address]
            if current_time - t < 3600  # Keep last hour
        ]
        
        self.failed_attempts[address].append(current_time)
        
        if len(self.failed_attempts[address]) >= self.max_failed_attempts:
            self.lockouts[address] = current_time + self.lockout_duration

    def _reset_failed_attempts(self, address: str):
        """Reset failed attempts after successful verification"""
        if address in self.failed_attempts:
            del self.failed_attempts[address]

    def setup_2fa(self, address: str) -> str:
        """Set up 2FA for wallet"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            address,
            issuer_name="VernaWallet"
        )
        return {
            "secret": secret,
            "uri": provisioning_uri
        }

    def verify_2fa(self, secret: str, code: str) -> bool:
        """Verify 2FA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    def check_transaction_limits(self, address: str, amount: int) -> bool:
        """Check if transaction is within limits"""
        current_time = time.time()
        day_start = current_time - (current_time % 86400)
        
        if address not in self.transaction_limits:
            self.transaction_limits[address] = {
                "daily_total": 0,
                "transactions": []
            }
            
        # Remove old transactions
        self.transaction_limits[address]["transactions"] = [
            tx for tx in self.transaction_limits[address]["transactions"]
            if tx["time"] >= day_start
        ]
        
        # Calculate daily total
        daily_total = sum(tx["amount"] for tx in self.transaction_limits[address]["transactions"])
        
        if daily_total + amount > self.daily_limit:
            return False
            
        # Record new transaction
        self.transaction_limits[address]["transactions"].append({
            "time": current_time,
            "amount": amount
        })
        
        return True

    def sign_transaction_with_2fa(
        self, tx: Dict[str, Any],
        encrypted_key_data: str,
        password: str,
        code: str,
        secret: str
    ) -> str:
        """Sign transaction with 2FA verification"""
        if not self.verify_2fa(secret, code):
            raise ValueError("Invalid 2FA code")
            
        key_data = json.loads(encrypted_key_data)
        key = self._derive_key(
            password.encode(),
            base64.b64decode(key_data["salt"])
        )
        private_key = self._decrypt_private_key(key_data["key"], key)
        
        # Check transaction limits
        amount = int(tx.get("value", 0))
        from_address = tx["from"]
        if not self.check_transaction_limits(from_address, amount):
            raise ValueError("Transaction exceeds daily limit")
            
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        return signed_tx.rawTransaction.hex()

    def export_wallet_secure(
        self,
        encrypted_key_data: str,
        password: str,
        export_password: str
    ) -> str:
        """Export wallet with additional encryption"""
        key_data = json.loads(encrypted_key_data)
        key = self._derive_key(
            password.encode(),
            base64.b64decode(key_data["salt"])
        )
        private_key = self._decrypt_private_key(key_data["key"], key)
        
        # Create new encryption for export
        export_salt = os.urandom(16)
        export_key = self._derive_key(export_password.encode(), export_salt)
        account = Account.from_key(private_key)
        
        # Create secure keystore
        keystore = {
            "version": 3,
            "id": str(uuid.uuid4()),
            "address": account.address,
            "crypto": self._create_keystore_crypto(private_key, export_key, export_salt)
        }
        
        return json.dumps(keystore)

    def _create_keystore_crypto(
        self,
        private_key: str,
        key: bytes,
        salt: bytes
    ) -> Dict[str, Any]:
        """Create secure keystore crypto section"""
        cipher = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, private_key.encode(), None)
        
        mac = hmac.new(
            key,
            nonce + ciphertext,
            hashlib.sha256
        ).hexdigest()
        
        return {
            "cipher": "aes-256-gcm",
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "cipherparams": {
                "nonce": base64.b64encode(nonce).decode()
            },
            "kdf": "pbkdf2",
            "kdfparams": {
                "dklen": 32,
                "c": 100000,
                "prf": "hmac-sha256",
                "salt": base64.b64encode(salt).decode()
            },
            "mac": mac
        }

    def create_wallet(self) -> Tuple[str, str]:
        """Create a new wallet"""
        account = Account.create()
        encrypted_key = self.encrypt_private_key(account.key.hex())
        return account.address, encrypted_key

    def recover_wallet(self, private_key: str) -> Tuple[str, str]:
        """Recover a wallet from private key"""
        account = Account.from_key(private_key)
        encrypted_key = self.encrypt_private_key(private_key)
        return account.address, encrypted_key

    def encrypt_private_key(self, private_key: str) -> str:
        """Encrypt a private key"""
        return self.fernet.encrypt(private_key.encode()).decode()

    def decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt a private key"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()

    def sign_transaction(self, tx: Dict[str, Any], encrypted_private_key: str) -> str:
        """Sign a transaction with a private key"""
        private_key = self.decrypt_private_key(encrypted_private_key)
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        return signed_tx.rawTransaction.hex()

    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """Verify a message signature"""
        try:
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            return recovered_address.lower() == address.lower()
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    def generate_nonce(self) -> str:
        """Generate a unique nonce for wallet authentication"""
        return str(uuid.uuid4())

    def sign_message(self, message: str, encrypted_private_key: str) -> str:
        """Sign a message with a private key"""
        private_key = self.decrypt_private_key(encrypted_private_key)
        message_hash = encode_defunct(text=message)
        signed_message = Account.sign_message(message_hash, private_key)
        return signed_message.signature.hex()

    def get_wallet_balance(self, address: str, web3_provider: Web3) -> Dict[str, Any]:
        """Get wallet balance and transaction count"""
        try:
            balance = web3_provider.eth.get_balance(address)
            tx_count = web3_provider.eth.get_transaction_count(address)
            return {
                "balance": str(balance),
                "transaction_count": tx_count
            }
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {
                "balance": "0",
                "transaction_count": 0
            }

    def export_wallet(self, encrypted_private_key: str, password: str) -> str:
        """Export wallet as encrypted JSON keystore"""
        private_key = self.decrypt_private_key(encrypted_private_key)
        account = Account.from_key(private_key)
        keystore = account.encrypt(password)
        return json.dumps(keystore)

    def import_wallet(self, keystore_json: str, password: str) -> Tuple[str, str]:
        """Import wallet from encrypted JSON keystore"""
        try:
            keystore = json.loads(keystore_json)
            account = Account.decrypt(keystore, password)
            encrypted_key = self.encrypt_private_key(account.hex())
            return Account.from_key(account).address, encrypted_key
        except Exception as e:
            logger.error(f"Error importing wallet: {e}")
            raise ValueError("Invalid keystore or password") 