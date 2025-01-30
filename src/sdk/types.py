from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Transaction:
    """Represents a blockchain transaction."""
    hash: str
    sender: str
    recipient: str
    amount: float
    timestamp: datetime
    shard_id: int
    status: str
    signature: Optional[str] = None
    nonce: Optional[int] = None
    gas_price: Optional[float] = None
    gas_limit: Optional[int] = None
    data: Optional[Dict] = None

@dataclass
class Block:
    """Represents a blockchain block."""
    number: int
    hash: str
    previous_hash: str
    timestamp: datetime
    transactions: List[Transaction]
    validator: str
    shard_id: int
    merkle_root: str
    state_root: str
    signature: Optional[str] = None
    size: Optional[int] = None
    gas_used: Optional[int] = None
    gas_limit: Optional[int] = None

@dataclass
class SmartContract:
    """Represents a deployed smart contract."""
    address: str
    contract_type: str
    creator: str
    creation_timestamp: datetime
    shard_id: int
    abi: Dict
    bytecode: str
    state: Optional[Dict] = None
    version: Optional[str] = None

@dataclass
class Validator:
    """Represents a blockchain validator."""
    address: str
    stake: float
    reputation: float
    total_blocks_validated: int
    is_active: bool
    last_active: datetime
    shard_id: int
    commission_rate: Optional[float] = None
    delegators: Optional[List[Dict]] = None

@dataclass
class CrossShardTransfer:
    """Represents a cross-shard transfer."""
    transfer_id: str
    from_shard: int
    to_shard: int
    transaction: Transaction
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    proof: Optional[Dict] = None

@dataclass
class BridgeTransfer:
    """Represents a cross-chain bridge transfer."""
    transfer_id: str
    source_chain: str
    target_chain: str
    amount: float
    sender: str
    recipient: str
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    proof: Optional[Dict] = None 