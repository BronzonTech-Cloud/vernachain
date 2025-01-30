from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Transaction(BaseModel):
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
    transfer_id: str
    from_shard: int
    to_shard: int
    transaction: Transaction
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    proof: Optional[Dict] = None

class BridgeTransfer(BaseModel):
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

# Request Models
class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float
    shard_id: int = Field(default=0)
    gas_price: Optional[float] = None
    gas_limit: Optional[int] = None
    data: Optional[Dict] = None

class ContractDeployRequest(BaseModel):
    contract_type: str
    params: Dict
    shard_id: int = Field(default=0)
    gas_limit: Optional[int] = None

class CrossShardTransferRequest(BaseModel):
    from_shard: int
    to_shard: int
    transaction: TransactionRequest

class BridgeTransferRequest(BaseModel):
    target_chain: str
    amount: float
    recipient: str
    gas_limit: Optional[int] = None 