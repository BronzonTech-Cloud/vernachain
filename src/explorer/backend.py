"""Vernachain Explorer Backend."""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Union, Set
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio
from ..networking.node import Node
from ..blockchain.blockchain import Blockchain

# Enhanced response models
class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[Dict]
    previous_hash: str
    validator: str
    hash: str
    size: int
    gas_used: int
    gas_limit: int
    transaction_count: int
    difficulty: int
    total_difficulty: int

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
    gas_price: float
    gas_used: Optional[int]
    nonce: int
    position_in_block: Optional[int]

class AddressResponse(BaseModel):
    address: str
    balance: float
    stake: float
    transaction_count: int
    is_validator: bool
    code: Optional[str]
    storage: Optional[Dict]
    nonce: int
    first_seen: float
    last_seen: float
    token_balances: List[Dict]

class NetworkStats(BaseModel):
    total_blocks: int
    total_transactions: int
    total_addresses: int
    total_validators: int
    total_shards: int
    average_block_time: float
    current_tps: float
    peak_tps: float
    total_staked: float
    current_difficulty: int
    hash_rate: float
    market_data: Optional[Dict]

class ValidatorResponse(BaseModel):
    address: str
    total_stake: float
    self_stake: float
    delegators: int
    blocks_validated: int
    uptime: float
    commission_rate: float
    rewards_earned: float
    performance_score: float
    status: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'stats': set(),
            'blocks': set(),
            'transactions': set(),
            'validators': set()
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.active_connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        self.active_connections[channel].remove(websocket)

    async def broadcast(self, message: dict, channel: str):
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.active_connections[channel].remove(connection)

manager = ConnectionManager()

# New analytics models
class GasAnalytics(BaseModel):
    average_gas_price: float
    gas_used_24h: int
    gas_limit_utilization: float
    gas_price_history: List[Dict[str, float]]

class TokenAnalytics(BaseModel):
    total_tokens: int
    active_tokens_24h: int
    token_transfers_24h: int
    top_tokens: List[Dict]
    token_creation_history: List[Dict]

class ShardAnalytics(BaseModel):
    total_shards: int
    active_shards: int
    cross_shard_txs_24h: int
    shard_sizes: List[int]
    shard_tps: List[float]

class NetworkAnalytics(BaseModel):
    node_distribution: Dict[str, int]
    network_latency: float
    peer_count_average: float
    bandwidth_usage: Dict[str, float]

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

# Cache for performance optimization
stats_cache = {}
blocks_cache = {}
cache_duration = timedelta(minutes=5)

def update_cache(key: str, data: any):
    stats_cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

def get_cached_data(key: str) -> Optional[any]:
    if key in stats_cache:
        cache_entry = stats_cache[key]
        if datetime.now() - cache_entry['timestamp'] < cache_duration:
            return cache_entry['data']
    return None

@app.get("/")
async def root():
    """Get enhanced blockchain information."""
    try:
        cached_stats = get_cached_data('network_stats')
        if cached_stats:
            return cached_stats

        blocks_count = len(blockchain.chain)
        tx_count = sum(len(block.transactions) for block in blockchain.chain)
        validators_count = len(blockchain.consensus.validators)
        shards_count = len(blockchain.master_chain.shards)
        
        # Calculate additional metrics
        recent_blocks = blockchain.chain[-100:]  # Last 100 blocks
        block_times = [
            recent_blocks[i].timestamp - recent_blocks[i-1].timestamp 
            for i in range(1, len(recent_blocks))
        ]
        avg_block_time = sum(block_times) / len(block_times) if block_times else 0
        
        # Calculate TPS
        recent_tx_count = sum(len(block.transactions) for block in recent_blocks)
        current_tps = recent_tx_count / (sum(block_times) if block_times else 1)
        
        stats = {
            "name": "Vernachain Explorer",
            "version": "0.2.0",
            "network": {
                "blocks": blocks_count,
                "transactions": tx_count,
                "validators": validators_count,
                "shards": shards_count,
                "average_block_time": avg_block_time,
                "current_tps": current_tps,
                "total_staked": blockchain.consensus.total_stake,
                "current_difficulty": blockchain.consensus.current_difficulty
            },
            "status": "running",
            "last_updated": datetime.now().isoformat()
        }
        
        update_cache('network_stats', stats)
        return stats
    except Exception as e:
        return {
            "name": "Vernachain Explorer",
            "version": "0.2.0",
            "status": "error",
            "error": str(e)
        }

@app.get("/stats")
async def get_network_stats() -> NetworkStats:
    """Get detailed network statistics."""
    cached_stats = get_cached_data('detailed_stats')
    if cached_stats:
        return cached_stats

    stats = NetworkStats(
        total_blocks=len(blockchain.chain),
        total_transactions=sum(len(block.transactions) for block in blockchain.chain),
        total_addresses=len(blockchain.state.accounts),
        total_validators=len(blockchain.consensus.validators),
        total_shards=len(blockchain.master_chain.shards),
        average_block_time=calculate_average_block_time(),
        current_tps=calculate_current_tps(),
        peak_tps=get_peak_tps(),
        total_staked=blockchain.consensus.total_stake,
        current_difficulty=blockchain.consensus.current_difficulty,
        hash_rate=calculate_hash_rate(),
        market_data=get_market_data()
    )
    
    update_cache('detailed_stats', stats)
    return stats

@app.get("/blocks")
async def get_blocks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    include_transactions: bool = False
) -> Dict:
    """Get paginated list of blocks with enhanced information."""
    total_blocks = len(blockchain.chain)
    start = total_blocks - (page * limit)
    end = start + limit
    start = max(0, start)
    
    blocks = blockchain.chain[start:end]
    
    response = {
        "blocks": [
            BlockResponse(
        index=block.index,
        timestamp=block.timestamp,
                transactions=block.transactions if include_transactions else [],
        previous_hash=block.previous_hash,
        validator=block.validator,
                hash=block.hash,
                size=calculate_block_size(block),
                gas_used=calculate_block_gas(block),
                gas_limit=block.gas_limit,
                transaction_count=len(block.transactions),
                difficulty=block.difficulty,
                total_difficulty=calculate_total_difficulty(block)
            )
            for block in reversed(blocks)
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_pages": (total_blocks + limit - 1) // limit,
            "total_blocks": total_blocks
        }
    }
    
    return response

@app.get("/blocks/{block_index}")
async def get_block(
    block_index: int,
    include_transactions: bool = True
) -> BlockResponse:
    """Get detailed block information."""
    try:
        block = blockchain.chain[block_index]
        return BlockResponse(
            index=block.index,
            timestamp=block.timestamp,
            transactions=block.transactions if include_transactions else [],
            previous_hash=block.previous_hash,
            validator=block.validator,
            hash=block.hash,
            size=calculate_block_size(block),
            gas_used=calculate_block_gas(block),
            gas_limit=block.gas_limit,
            transaction_count=len(block.transactions),
            difficulty=block.difficulty,
            total_difficulty=calculate_total_difficulty(block)
        )
    except IndexError:
        raise HTTPException(status_code=404, detail="Block not found")

@app.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    address: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "desc"
) -> Dict:
    """Get paginated list of transactions with filtering."""
    transactions = []
    
    # Collect all transactions
    for block in reversed(blockchain.chain):
        for idx, tx in enumerate(block.transactions):
            if (
                (not address or address in [tx.get("from_address"), tx.get("to_address")]) and
                (not type or tx["type"] == type) and
                (not status or status == "confirmed")
            ):
                transactions.append({
            **tx,
            "block_index": block.index,
                    "status": "confirmed",
                    "position_in_block": idx,
                    "gas_used": calculate_transaction_gas(tx)
                })
    
    # Add pending transactions if requested
    if not status or status == "pending":
        pending_txs = [
            {
        **tx,
        "block_index": None,
                "status": "pending",
                "position_in_block": None,
                "gas_used": None
            }
            for tx in blockchain.transaction_pool.transactions
            if (not address or address in [tx.get("from_address"), tx.get("to_address")]) and
               (not type or tx["type"] == type)
        ]
        transactions.extend(pending_txs)
    
    # Sort transactions
    transactions.sort(key=lambda x: (x["block_index"] or float('inf'), x["timestamp"]),
                     reverse=(sort == "desc"))
    
    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated_txs = transactions[start:end]
    
    return {
        "transactions": [TransactionResponse(**tx) for tx in paginated_txs],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_pages": (len(transactions) + limit - 1) // limit,
            "total_transactions": len(transactions)
        }
    }

@app.get("/address/{address}")
async def get_address(address: str) -> AddressResponse:
    """Get detailed address information."""
    balance = 0
    stake = 0
    transaction_count = 0
    first_seen = None
    last_seen = None
    nonce = 0
    
    # Calculate metrics
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx["from_address"] == address or tx["to_address"] == address:
                timestamp = tx["timestamp"]
                if first_seen is None or timestamp < first_seen:
                    first_seen = timestamp
                if last_seen is None or timestamp > last_seen:
                    last_seen = timestamp
                
            if tx["from_address"] == address:
                transaction_count += 1
                nonce = max(nonce, tx.get("nonce", 0))
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
    
    # Get contract information if it's a contract address
    code = blockchain.state.get_code(address)
    storage = blockchain.state.get_storage(address) if code else None
    
    # Get token balances
    token_balances = get_token_balances(address)
    
    # Check if address is a validator
    is_validator = any(v.address == address for v in blockchain.consensus.validators)
    
    return AddressResponse(
        address=address,
        balance=balance,
        stake=stake,
        transaction_count=transaction_count,
        is_validator=is_validator,
        code=code,
        storage=storage,
        nonce=nonce,
        first_seen=first_seen or 0,
        last_seen=last_seen or 0,
        token_balances=token_balances
    )

@app.get("/validators")
async def get_validators() -> List[ValidatorResponse]:
    """Get list of validators with detailed information."""
    validators = []
    
    for validator in blockchain.consensus.validators:
        # Calculate validator metrics
        blocks_validated = sum(
            1 for block in blockchain.chain
            if block.validator == validator.address
        )
        
        # Calculate uptime
        uptime = calculate_validator_uptime(validator.address)
        
        # Get delegator information
        delegators = get_validator_delegators(validator.address)
        
        # Calculate rewards
        rewards = calculate_validator_rewards(validator.address)
        
        validators.append(ValidatorResponse(
            address=validator.address,
            total_stake=validator.total_stake,
            self_stake=validator.self_stake,
            delegators=len(delegators),
            blocks_validated=blocks_validated,
            uptime=uptime,
            commission_rate=validator.commission_rate,
            rewards_earned=rewards,
            performance_score=calculate_validator_performance(validator.address),
            status=get_validator_status(validator.address)
        ))
    
    return validators

@app.get("/search/{query}")
async def search(query: str):
    """Enhanced search for blocks, transactions, addresses, or validators."""
    results = {
        "blocks": [],
        "transactions": [],
        "addresses": [],
        "validators": []
    }
    
    # Search blocks
    try:
        block_index = int(query)
        if 0 <= block_index < len(blockchain.chain):
            block = blockchain.chain[block_index]
            results["blocks"].append({
                "index": block.index,
                "hash": block.hash,
                "timestamp": block.timestamp,
                "transaction_count": len(block.transactions)
            })
    except ValueError:
        # Search by hash
        for block in blockchain.chain:
            if block.hash.startswith(query.lower()):
                results["blocks"].append({
                    "index": block.index,
                    "hash": block.hash,
                    "timestamp": block.timestamp,
                    "transaction_count": len(block.transactions)
                })
    
    # Search transactions
    for block in blockchain.chain:
        for tx in block.transactions:
            if (tx["signature"].startswith(query.lower()) or
                tx.get("from_address", "").startswith(query.lower()) or
                tx.get("to_address", "").startswith(query.lower())):
                results["transactions"].append({
                    "hash": tx["signature"],
                    "type": tx["type"],
                    "amount": tx["amount"],
                    "block_index": block.index,
                    "timestamp": tx["timestamp"]
                })
    
    # Search addresses and validators
    if len(query) >= 32:  # Only search if query is long enough
        address_info = get_address_info(query.lower())
        if address_info:
            results["addresses"].append(address_info)
        
        validator_info = get_validator_info(query.lower())
        if validator_info:
            results["validators"].append(validator_info)
    
    return results

@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    await manager.connect(websocket, 'stats')
    try:
        while True:
            stats = await get_network_stats()
            await websocket.send_json(stats.dict())
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'stats')

@app.websocket("/ws/blocks")
async def websocket_blocks(websocket: WebSocket):
    await manager.connect(websocket, 'blocks')
    try:
        last_block = len(blockchain.chain)
        while True:
            current_block = len(blockchain.chain)
            if current_block > last_block:
                block = blockchain.chain[-1]
                await websocket.send_json({
                    "type": "new_block",
                    "data": BlockResponse(**block.__dict__).dict()
                })
                last_block = current_block
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'blocks')

@app.get("/analytics/gas")
async def get_gas_analytics() -> GasAnalytics:
    """Get detailed gas usage analytics."""
    cached_data = get_cached_data('gas_analytics')
    if cached_data:
        return cached_data

    recent_blocks = blockchain.chain[-1000:]  # Last 1000 blocks
    gas_prices = []
    total_gas_used = 0
    total_gas_limit = 0

    for block in recent_blocks:
        block_gas_used = calculate_block_gas(block)
        total_gas_used += block_gas_used
        total_gas_limit += block.gas_limit
        avg_gas_price = sum(calculate_transaction_gas(tx) for tx in block.transactions) / len(block.transactions) if block.transactions else 0
        gas_prices.append({
            "timestamp": block.timestamp,
            "price": avg_gas_price
        })

    analytics = GasAnalytics(
        average_gas_price=sum(g["price"] for g in gas_prices) / len(gas_prices) if gas_prices else 0,
        gas_used_24h=total_gas_used,
        gas_limit_utilization=total_gas_used / total_gas_limit if total_gas_limit else 0,
        gas_price_history=gas_prices
    )
    
    update_cache('gas_analytics', analytics)
    return analytics

@app.get("/analytics/tokens")
async def get_token_analytics() -> TokenAnalytics:
    """Get detailed token analytics."""
    cached_data = get_cached_data('token_analytics')
    if cached_data:
        return cached_data

    # Implementation depends on your token tracking system
    analytics = TokenAnalytics(
        total_tokens=len(blockchain.state.tokens),
        active_tokens_24h=calculate_active_tokens_24h(),
        token_transfers_24h=calculate_token_transfers_24h(),
        top_tokens=get_top_tokens(),
        token_creation_history=get_token_creation_history()
    )
    
    update_cache('token_analytics', analytics)
    return analytics

@app.get("/analytics/shards")
async def get_shard_analytics() -> ShardAnalytics:
    """Get detailed shard analytics."""
    cached_data = get_cached_data('shard_analytics')
    if cached_data:
        return cached_data

    analytics = ShardAnalytics(
        total_shards=len(blockchain.master_chain.shards),
        active_shards=count_active_shards(),
        cross_shard_txs_24h=count_cross_shard_transactions_24h(),
        shard_sizes=[len(shard.chain) for shard in blockchain.master_chain.shards],
        shard_tps=calculate_shard_tps()
    )
    
    update_cache('shard_analytics', analytics)
    return analytics

@app.get("/analytics/network")
async def get_network_analytics() -> NetworkAnalytics:
    """Get detailed network analytics."""
    cached_data = get_cached_data('network_analytics')
    if cached_data:
        return cached_data

    analytics = NetworkAnalytics(
        node_distribution=get_node_distribution(),
        network_latency=calculate_network_latency(),
        peer_count_average=calculate_average_peer_count(),
        bandwidth_usage=calculate_bandwidth_usage()
    )
    
    update_cache('network_analytics', analytics)
    return analytics

# Helper functions
def calculate_block_size(block) -> int:
    """Calculate block size in bytes."""
    # Implementation depends on your block structure
    pass

def calculate_block_gas(block) -> int:
    """Calculate total gas used in block."""
    return sum(calculate_transaction_gas(tx) for tx in block.transactions)

def calculate_transaction_gas(tx) -> int:
    """Calculate gas used by transaction."""
    # Implementation depends on your transaction structure
    pass

def calculate_total_difficulty(block) -> int:
    """Calculate total difficulty up to this block."""
    # Implementation depends on your consensus mechanism
    pass

def calculate_average_block_time() -> float:
    """Calculate average block time over last 100 blocks."""
    pass

def calculate_current_tps() -> float:
    """Calculate current transactions per second."""
    pass

def get_peak_tps() -> float:
    """Get peak TPS in the last 24 hours."""
    pass

def calculate_hash_rate() -> float:
    """Calculate network hash rate."""
    pass

def get_market_data() -> Dict:
    """Get market data from external sources."""
    pass

def get_token_balances(address: str) -> List[Dict]:
    """Get token balances for address."""
    pass

def calculate_validator_uptime(address: str) -> float:
    """Calculate validator uptime percentage."""
    pass

def get_validator_delegators(address: str) -> List[Dict]:
    """Get list of delegators for validator."""
    pass

def calculate_validator_rewards(address: str) -> float:
    """Calculate total rewards earned by validator."""
    pass

def calculate_validator_performance(address: str) -> float:
    """Calculate validator performance score."""
    pass

def get_validator_status(address: str) -> str:
    """Get current validator status."""
    pass

def get_address_info(address: str) -> Optional[Dict]:
    """Get basic address information."""
    pass

def get_validator_info(address: str) -> Optional[Dict]:
    """Get basic validator information."""
    pass

def calculate_active_tokens_24h() -> int:
    """Calculate number of tokens with transfers in last 24h."""
    pass

def calculate_token_transfers_24h() -> int:
    """Calculate total token transfers in last 24h."""
    pass

def get_top_tokens() -> List[Dict]:
    """Get list of top tokens by various metrics."""
    pass

def get_token_creation_history() -> List[Dict]:
    """Get token creation history."""
    pass

def count_active_shards() -> int:
    """Count number of active shards."""
    pass

def count_cross_shard_transactions_24h() -> int:
    """Count cross-shard transactions in last 24h."""
    pass

def calculate_shard_tps() -> List[float]:
    """Calculate TPS for each shard."""
    pass

def get_node_distribution() -> Dict[str, int]:
    """Get geographical distribution of nodes."""
    pass

def calculate_network_latency() -> float:
    """Calculate average network latency."""
    pass

def calculate_average_peer_count() -> float:
    """Calculate average peer count per node."""
    pass

def calculate_bandwidth_usage() -> Dict[str, float]:
    """Calculate network bandwidth usage."""
    pass 