from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class Transaction(BaseModel):
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

class Block(BaseModel):
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

class SmartContract(BaseModel):
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

class Validator(BaseModel):
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

class CrossShardTransfer(BaseModel):
    """Represents a cross-shard transfer."""
    transfer_id: str
    from_shard: int
    to_shard: int
    transaction: Transaction
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    proof: Optional[Dict] = None

class BridgeTransfer(BaseModel):
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

# Additional type definitions for request/response models
class TransactionRequest(BaseModel):
    """Model for transaction creation request."""
    sender: str
    recipient: str
    amount: float
    shard_id: int = Field(default=0)
    gas_price: Optional[float] = None
    gas_limit: Optional[int] = None
    data: Optional[Dict] = None

class ContractDeployRequest(BaseModel):
    """Model for contract deployment request."""
    contract_type: str
    params: Dict
    shard_id: int = Field(default=0)
    gas_limit: Optional[int] = None

class CrossShardTransferRequest(BaseModel):
    """Model for cross-shard transfer request."""
    from_shard: int
    to_shard: int
    transaction: TransactionRequest

class BridgeTransferRequest(BaseModel):
    """Model for bridge transfer request."""
    target_chain: str
    amount: float
    recipient: str
    gas_limit: Optional[int] = None