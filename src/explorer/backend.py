from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from pydantic import BaseModel
from ..networking.node import Node
from ..blockchain.blockchain import Blockchain

class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[Dict]
    previous_hash: str
    validator: str
    hash: str

class TransactionResponse(BaseModel):
    type: str
    from_address: Optional[str]
    to_address: Optional[str]
    amount: float
    data: Optional[str]
    timestamp: float
    signature: str
    block_index: Optional[int]
    status: str

class AddressResponse(BaseModel):
    address: str
    balance: float
    stake: float
    transaction_count: int
    is_validator: bool

app = FastAPI(title="Vernachain Explorer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize blockchain node
node = Node()
blockchain = Blockchain()

@app.get("/")
async def root():
    """Get blockchain stats."""
    return {
        "block_height": len(blockchain.chain),
        "transaction_count": sum(len(block.transactions) for block in blockchain.chain),
        "validator_count": len(blockchain.consensus.validators),
        "network_stats": node.get_network_stats()
    }

@app.get("/blocks")
async def get_blocks(page: int = 1, limit: int = 10) -> List[BlockResponse]:
    """Get paginated list of blocks."""
    start = (page - 1) * limit
    end = start + limit
    blocks = blockchain.chain[start:end]
    
    return [BlockResponse(
        index=block.index,
        timestamp=block.timestamp,
        transactions=block.transactions,
        previous_hash=block.previous_hash,
        validator=block.validator,
        hash=block.hash
    ) for block in blocks]

@app.get("/blocks/{block_index}")
async def get_block(block_index: int) -> BlockResponse:
    """Get block by index."""
    try:
        block = blockchain.chain[block_index]
        return BlockResponse(
            index=block.index,
            timestamp=block.timestamp,
            transactions=block.transactions,
            previous_hash=block.previous_hash,
            validator=block.validator,
            hash=block.hash
        )
    except IndexError:
        raise HTTPException(status_code=404, detail="Block not found")

@app.get("/transactions")
async def get_transactions(page: int = 1, limit: int = 20) -> List[TransactionResponse]:
    """Get paginated list of transactions."""
    transactions = []
    for block in reversed(blockchain.chain):
        transactions.extend([{
            **tx,
            "block_index": block.index,
            "status": "confirmed"
        } for tx in block.transactions])
    
    # Add pending transactions
    transactions.extend([{
        **tx,
        "block_index": None,
        "status": "pending"
    } for tx in blockchain.transaction_pool.transactions])
    
    start = (page - 1) * limit
    end = start + limit
    return [TransactionResponse(**tx) for tx in transactions[start:end]]

@app.get("/transactions/{tx_hash}")
async def get_transaction(tx_hash: str) -> TransactionResponse:
    """Get transaction by hash (signature)."""
    # Search in confirmed transactions
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx["signature"] == tx_hash:
                return TransactionResponse(
                    **tx,
                    block_index=block.index,
                    status="confirmed"
                )
    
    # Search in pending transactions
    for tx in blockchain.transaction_pool.transactions:
        if tx["signature"] == tx_hash:
            return TransactionResponse(
                **tx,
                block_index=None,
                status="pending"
            )
            
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/address/{address}")
async def get_address(address: str) -> AddressResponse:
    """Get address details."""
    # Calculate balance and transaction count
    balance = 0
    stake = 0
    transaction_count = 0
    
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx["from_address"] == address:
                transaction_count += 1
                if tx["type"] == "transfer":
                    balance -= tx["amount"]
                elif tx["type"] == "stake":
                    balance -= tx["amount"]
                    stake += tx["amount"]
                elif tx["type"] == "unstake":
                    stake -= tx["amount"]
                    balance += tx["amount"]
            if tx["to_address"] == address:
                transaction_count += 1
                balance += tx["amount"]
    
    # Check if address is a validator
    is_validator = any(v.address == address for v in blockchain.consensus.validators)
    
    return AddressResponse(
        address=address,
        balance=balance,
        stake=stake,
        transaction_count=transaction_count,
        is_validator=is_validator
    )

@app.get("/search/{query}")
async def search(query: str):
    """Search for blocks, transactions, or addresses."""
    results = {
        "blocks": [],
        "transactions": [],
        "addresses": []
    }
    
    # Search blocks by index or hash
    try:
        block_index = int(query)
        if 0 <= block_index < len(blockchain.chain):
            block = blockchain.chain[block_index]
            results["blocks"].append({
                "index": block.index,
                "hash": block.hash,
                "timestamp": block.timestamp
            })
    except ValueError:
        # Search by hash
        for block in blockchain.chain:
            if block.hash.startswith(query):
                results["blocks"].append({
                    "index": block.index,
                    "hash": block.hash,
                    "timestamp": block.timestamp
                })
    
    # Search transactions
    for block in blockchain.chain:
        for tx in block.transactions:
            if (tx["signature"].startswith(query) or
                tx.get("from_address", "").startswith(query) or
                tx.get("to_address", "").startswith(query)):
                results["transactions"].append({
                    "hash": tx["signature"],
                    "type": tx["type"],
                    "amount": tx["amount"],
                    "block_index": block.index
                })
    
    # Search addresses
    if len(query) >= 32:  # Only search if query is long enough to be an address
        for validator in blockchain.consensus.validators:
            if validator.address.startswith(query):
                results["addresses"].append({
                    "address": validator.address,
                    "is_validator": True
                })
    
    return results

@app.get("/validators")
async def get_validators():
    """Get list of current validators."""
    return [{
        "address": v.address,
        "stake": v.stake,
        "is_active": v.is_active,
        "last_block_time": v.last_block_time
    } for v in blockchain.consensus.validators]

@app.get("/shards")
async def get_shards():
    """Get shard information."""
    return {
        "shard_count": len(blockchain.shards),
        "shards": [{
            "id": shard.id,
            "validator_count": len(shard.validators),
            "transaction_count": sum(len(block.transactions) for block in shard.chain),
            "latest_block": {
                "index": shard.chain[-1].index,
                "timestamp": shard.chain[-1].timestamp
            } if shard.chain else None
        } for shard in blockchain.shards]
    } 