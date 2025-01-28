import hashlib
import json
from time import time
from typing import List, Dict, Any


class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], timestamp: float,
                 previous_hash: str, validator: str):
        """
        Initialize a new block.
        
        Args:
            index: Block number in the chain
            transactions: List of transaction dictionaries
            timestamp: Block creation timestamp
            previous_hash: Hash of the previous block
            validator: Address of the validator who created the block
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block using SHA-256.
        
        Returns:
            str: Hexadecimal string of the block's hash
        """
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "validator": self.validator
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """
        Mine the block by finding a nonce that satisfies the difficulty requirement.
        
        Args:
            difficulty: Number of leading zeros required in the hash
        """
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the block to a dictionary representation.
        
        Returns:
            Dict containing the block's data
        """
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(block_dict: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from a dictionary representation.
        
        Args:
            block_dict: Dictionary containing block data
            
        Returns:
            Block: A new Block instance
        """
        block = Block(
            index=block_dict["index"],
            transactions=block_dict["transactions"],
            timestamp=block_dict["timestamp"],
            previous_hash=block_dict["previous_hash"],
            validator=block_dict["validator"]
        )
        block.hash = block_dict["hash"]
        return block

    def is_valid(self, difficulty: int) -> bool:
        """
        Validate the block's hash and proof of work.
        
        Args:
            difficulty: Number of leading zeros required in the hash
            
        Returns:
            bool: True if the block is valid, False otherwise
        """
        if self.hash != self.calculate_hash():
            return False
            
        if self.hash[:difficulty] != "0" * difficulty:
            return False
            
        return True 