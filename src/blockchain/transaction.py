"""Transaction implementation for Vernachain."""

from typing import Dict, Any
from datetime import datetime

from src.utils.crypto import sign_message, verify_signature, hash_data
from src.utils.validation import is_valid_address
from src.utils.serialization import serialize_transaction
from src.utils.logging import blockchain_logger

class Transaction:
    def __init__(self, from_address: str, to_address: str, value: float, nonce: int):
        """Initialize a new transaction.
        
        Args:
            from_address: Sender's address
            to_address: Recipient's address
            value: Amount to transfer
            nonce: Transaction nonce (prevents replay attacks)
        """
        if not is_valid_address(from_address) or not is_valid_address(to_address):
            blockchain_logger.error("Invalid address in transaction")
            raise ValueError("Invalid address")
            
        if value <= 0:
            blockchain_logger.error(f"Invalid transaction value: {value}")
            raise ValueError("Value must be positive")
            
        self.from_address = from_address
        self.to_address = to_address
        self.value = value
        self.nonce = nonce
        self.timestamp = datetime.now()
        self.signature = None
        
        # Calculate transaction hash
        self.hash = self._calculate_hash()
        
        blockchain_logger.debug(f"Transaction created: {self.hash}")
        
    def sign(self, private_key: str) -> None:
        """Sign the transaction with sender's private key."""
        if not self.signature:  # Only sign if not already signed
            message = serialize_transaction(self.to_dict())
            self.signature = sign_message(private_key, message)
            blockchain_logger.debug(f"Transaction signed: {self.hash}")
            
    def verify(self) -> bool:
        """Verify the transaction signature."""
        if not self.signature:
            blockchain_logger.error("Transaction not signed")
            return False
            
        try:
            message = serialize_transaction(self.to_dict())
            return verify_signature(self.from_address, message, self.signature)
        except Exception as e:
            blockchain_logger.error(f"Transaction verification failed: {e}")
            return False
            
    def _calculate_hash(self) -> str:
        """Calculate transaction hash."""
        tx_dict = self.to_dict()
        tx_dict.pop('signature', None)  # Remove signature from hash calculation
        tx_dict.pop('hash', None)  # Remove hash from hash calculation
        
        return hash_data(serialize_transaction(tx_dict))
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            'from': self.from_address,
            'to': self.to_address,
            'value': self.value,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        tx = cls(
            from_address=data['from'],
            to_address=data['to'],
            value=data['value'],
            nonce=data['nonce']
        )
        tx.timestamp = data['timestamp']
        tx.signature = data['signature']
        tx.hash = data['hash']
        return tx 