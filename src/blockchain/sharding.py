from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import hashlib
import json
from .block import Block
from .transaction import Transaction
from src.utils.serialization import serialize_transaction
from src.utils.validation import is_valid_transaction
import time


@dataclass
class ShardInfo:
    """Information about a shard in the network."""
    shard_id: int
    validator_set: Set[str] = field(default_factory=set)
    state_root: str = ""  # Merkle root of shard's state
    last_block_height: int = 0


@dataclass
class CrossShardMessage:
    """Message for cross-shard communication."""
    from_shard: int
    to_shard: int
    transaction_hash: str
    merkle_proof: List[str]
    status: str = "pending"  # pending, completed, failed


class ShardChain:
    """Represents a single shard chain."""
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.chain: List[Block] = []
        self.pending_messages: List[CrossShardMessage] = []
        self.processed_messages: Dict[str, CrossShardMessage] = {}
        
    def add_block(self, block: Block) -> bool:
        """Add a new block to the shard chain."""
        if self.is_valid_block(block):
            self.chain.append(block)
            return True
        return False
        
    def is_valid_block(self, block: Block) -> bool:
        """Validate a block for the shard chain."""
        if not self.chain:
            return block.index == 0
            
        prev_block = self.chain[-1]
        return (block.index == len(self.chain) and
                block.previous_hash == prev_block.hash)
                
    def get_state_root(self) -> str:
        """Calculate the Merkle root of the shard's state."""
        if not self.chain:
            return hashlib.sha256(b"empty").hexdigest()
            
        state_items = []
        for block in self.chain:
            for tx in block.transactions:
                state_items.append(json.dumps(tx, sort_keys=True))
                
        return self._calculate_merkle_root(state_items)
        
    @staticmethod
    def _calculate_merkle_root(items: List[str]) -> str:
        """Calculate Merkle root from a list of items."""
        if not items:
            return hashlib.sha256(b"empty").hexdigest()
            
        # Hash all items
        hashes = [hashlib.sha256(item.encode()).hexdigest() for item in items]
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(next_hash)
            hashes = next_level
            
        return hashes[0]

    def process_cross_shard_transaction(self, message: CrossShardMessage, transaction: Dict) -> bool:
        """
        Process a cross-shard transaction.
        
        Args:
            message: Cross-shard message containing transaction details
            transaction: The transaction to process
            
        Returns:
            bool: True if transaction processed successfully
        """
        # Validate the transaction
        if not is_valid_transaction(transaction):
            message.status = "failed"
            return False
            
        # Verify the transaction belongs to this shard
        if message.to_shard != self.shard_id:
            message.status = "failed"
            return False
            
        # Verify merkle proof
        if not self._verify_merkle_proof(transaction, message.merkle_proof):
            message.status = "failed"
            return False
            
        # Create a new block for the cross-shard transaction
        new_block = Block(
            index=len(self.chain),
            transactions=[serialize_transaction(transaction)],
            timestamp=time.time(),
            previous_hash=self.chain[-1].hash if self.chain else "0" * 64,
            validator="system"  # Cross-shard transactions are processed by the system
        )
        
        # Add block to chain
        if not self.add_block(new_block):
            message.status = "failed"
            return False
            
        message.status = "completed"
        return True
        
    def _verify_merkle_proof(self, transaction: Dict, proof: List[str]) -> bool:
        """Verify a merkle proof for a transaction."""
        tx_hash = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()
        
        current_hash = tx_hash
        for proof_element in proof:
            combined = current_hash + proof_element
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
            
        return current_hash == self.get_state_root()


class MasterChain:
    """Represents the master chain that coordinates shards."""
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shards: Dict[int, ShardInfo] = {}
        self.chain: List[Block] = []
        self.cross_shard_messages: Dict[str, CrossShardMessage] = {}
        
        # Initialize shards
        for i in range(num_shards):
            self.shards[i] = ShardInfo(shard_id=i)
            
    def assign_validator_to_shard(self, validator_address: str, shard_id: int) -> bool:
        """Assign a validator to a specific shard."""
        if shard_id not in self.shards:
            return False
            
        self.shards[shard_id].validator_set.add(validator_address)
        return True
        
    def update_shard_info(self, shard_id: int, state_root: str, 
                         block_height: int) -> bool:
        """Update the state information of a shard."""
        if shard_id not in self.shards:
            return False
            
        shard = self.shards[shard_id]
        shard.state_root = state_root
        shard.last_block_height = block_height
        return True
        
    def get_shard_for_address(self, address: str) -> int:
        """Determine which shard an address belongs to."""
        # Simple sharding by address hash
        address_hash = int(hashlib.sha256(address.encode()).hexdigest(), 16)
        return address_hash % self.num_shards
        
    def create_cross_shard_message(self, from_shard: int, to_shard: int,
                                 tx_hash: str, merkle_proof: List[str]) -> Optional[str]:
        """Create a new cross-shard message."""
        if from_shard not in self.shards or to_shard not in self.shards:
            return None
            
        message = CrossShardMessage(
            from_shard=from_shard,
            to_shard=to_shard,
            transaction_hash=tx_hash,
            merkle_proof=merkle_proof
        )
        
        message_hash = hashlib.sha256(
            f"{from_shard}{to_shard}{tx_hash}".encode()
        ).hexdigest()
        
        self.cross_shard_messages[message_hash] = message
        return message_hash
        
    def verify_cross_shard_message(self, message_hash: str) -> bool:
        """Verify a cross-shard message using its Merkle proof."""
        if message_hash not in self.cross_shard_messages:
            return False
            
        message = self.cross_shard_messages[message_hash]
        from_shard = self.shards.get(message.from_shard)
        
        if not from_shard:
            return False
            
        # Verify the Merkle proof
        current_hash = message.transaction_hash
        for proof_element in message.merkle_proof:
            combined = current_hash + proof_element
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
            
        return current_hash == from_shard.state_root
        
    def complete_cross_shard_message(self, message_hash: str, success: bool) -> bool:
        """Mark a cross-shard message as completed or failed."""
        if message_hash not in self.cross_shard_messages:
            return False
            
        message = self.cross_shard_messages[message_hash]
        message.status = "completed" if success else "failed"
        return True 