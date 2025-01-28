"""
API Service for Vernachain.

This module provides RESTful API endpoints for blockchain interaction.
"""

from fastapi import FastAPI, Depends, HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from datetime import datetime
import time
from pydantic import BaseModel, Field

# Models for request/response
class TransactionRequest(BaseModel):
    to_address: str = Field(..., description="Recipient address")
    value: float = Field(..., description="Amount to send")
    private_key: str = Field(..., description="Sender's private key")
    gas_limit: Optional[int] = Field(None, description="Optional gas limit")
    data: Optional[str] = Field(None, description="Optional contract data")

class TransactionResponse(BaseModel):
    transaction_hash: str
    status: str
    timestamp: datetime

class BlockResponse(BaseModel):
    number: int
    hash: str
    timestamp: datetime
    transactions: List[str]
    validator: str
    size: int

class BalanceResponse(BaseModel):
    address: str
    balance: float
    last_updated: datetime

class ContractDeployRequest(BaseModel):
    bytecode: str = Field(..., description="Contract bytecode")
    abi: Dict = Field(..., description="Contract ABI")
    private_key: str = Field(..., description="Deployer's private key")
    constructor_args: Optional[List] = Field(None, description="Constructor arguments")
    gas_limit: Optional[int] = Field(None, description="Gas limit for deployment")

class ContractCallRequest(BaseModel):
    function_name: str = Field(..., description="Function to call")
    args: List = Field(default=[], description="Function arguments")
    abi: Dict = Field(..., description="Contract ABI")

class BridgeTransferRequest(BaseModel):
    from_chain: str = Field(..., description="Source chain")
    to_chain: str = Field(..., description="Target chain")
    token: str = Field(..., description="Token symbol")
    amount: float = Field(..., description="Amount to transfer")
    to_address: str = Field(..., description="Recipient address")
    private_key: str = Field(..., description="Sender's private key")

# Initialize FastAPI
app = FastAPI(
    title="Vernachain API",
    description="Official API for Vernachain blockchain",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
RATE_LIMIT_WINDOW = 3600  # 1 hour
RATE_LIMIT_MAX_REQUESTS = 1000

# Rate limiting storage
rate_limits: Dict[str, Dict] = {}

def check_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Validate API key and check rate limits."""
    if api_key not in rate_limits:
        rate_limits[api_key] = {
            'requests': 0,
            'window_start': time.time()
        }
    
    # Reset window if needed
    if time.time() - rate_limits[api_key]['window_start'] > RATE_LIMIT_WINDOW:
        rate_limits[api_key]['requests'] = 0
        rate_limits[api_key]['window_start'] = time.time()
    
    # Check rate limit
    if rate_limits[api_key]['requests'] >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    rate_limits[api_key]['requests'] += 1
    return api_key

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

# Blockchain Routes
@app.post("/api/v1/transaction", response_model=TransactionResponse)
async def send_transaction(
    request: TransactionRequest,
    api_key: str = Depends(check_api_key)
):
    """Submit a new transaction to the blockchain."""
    try:
        # Implementation will connect to blockchain node
        return {
            "transaction_hash": "0x...",
            "status": "pending",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send transaction: {str(e)}"
        )

@app.get("/api/v1/transaction/{tx_hash}")
async def get_transaction(tx_hash: str, api_key: str = Depends(check_api_key)):
    """Get transaction details by hash."""
    try:
        # Implementation will connect to blockchain node
        return {
            "hash": tx_hash,
            "from_address": "0x...",
            "to_address": "0x...",
            "value": 1.0,
            "status": "confirmed",
            "timestamp": datetime.utcnow(),
            "block_number": 1000,
            "gas_used": 21000
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction not found: {str(e)}"
        )

@app.get("/api/v1/balance/{address}", response_model=BalanceResponse)
async def get_balance(
    address: str,
    api_key: str = Depends(check_api_key)
):
    """Get balance for a wallet address."""
    try:
        # Implementation will connect to blockchain node
        return {
            "address": address,
            "balance": 100.0,  # Mock data
            "last_updated": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address not found: {str(e)}"
        )

@app.get("/api/v1/block/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: int,
    api_key: str = Depends(check_api_key)
):
    """Get block details by ID."""
    try:
        # Implementation will connect to blockchain node
        return {
            "number": block_id,
            "hash": "0x...",
            "timestamp": datetime.utcnow(),
            "transactions": [],
            "validator": "0x...",
            "size": 1000
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block not found: {str(e)}"
        )

# Smart Contract Routes
@app.post("/api/v1/contract/deploy")
async def deploy_contract(
    request: ContractDeployRequest,
    api_key: str = Depends(check_api_key)
):
    """Deploy a new smart contract."""
    try:
        # Implementation will connect to blockchain node
        return {
            "contract_address": "0x...",
            "transaction_hash": "0x...",
            "deployer": "0x...",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract deployment failed: {str(e)}"
        )

@app.post("/api/v1/contract/{address}/call")
async def call_contract(
    address: str,
    request: ContractCallRequest,
    api_key: str = Depends(check_api_key)
):
    """Call a contract function."""
    try:
        # Implementation will connect to blockchain node
        return {
            "result": None,  # Function result
            "transaction_hash": "0x...",  # If state-changing function
            "gas_used": 21000
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract call failed: {str(e)}"
        )

# Bridge Routes
@app.post("/api/v1/bridge/transfer")
async def bridge_transfer(
    request: BridgeTransferRequest,
    api_key: str = Depends(check_api_key)
):
    """Initiate a cross-chain transfer."""
    try:
        # Implementation will connect to bridge
        return {
            "bridge_tx_hash": "0x...",
            "from_chain_tx": "0x...",
            "status": "pending",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bridge transfer failed: {str(e)}"
        )

@app.get("/api/v1/bridge/transaction/{tx_hash}")
async def get_bridge_transaction(
    tx_hash: str,
    api_key: str = Depends(check_api_key)
):
    """Get bridge transaction status."""
    try:
        # Implementation will connect to bridge
        return {
            "bridge_tx_hash": tx_hash,
            "from_chain_tx": "0x...",
            "to_chain_tx": "0x...",
            "status": "completed",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bridge transaction not found: {str(e)}"
        )

# Network Stats Routes
@app.get("/api/v1/stats")
async def get_network_stats(api_key: str = Depends(check_api_key)):
    """Get network statistics."""
    try:
        return {
            "total_transactions": 1000000,
            "total_blocks": 50000,
            "active_validators": 100,
            "tps": 1000,
            "market_data": {
                "price": 10.0,
                "market_cap": 1000000000,
                "volume_24h": 50000000
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get network stats: {str(e)}"
        )

# Health check
@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# API Stats
@app.get("/api/stats")
async def get_api_stats(api_key: str = Depends(check_api_key)):
    """Get API usage statistics."""
    if api_key in rate_limits:
        return {
            "requests": rate_limits[api_key]['requests'],
            "window_start": datetime.fromtimestamp(rate_limits[api_key]['window_start']),
            "remaining": RATE_LIMIT_MAX_REQUESTS - rate_limits[api_key]['requests']
        }
    return {
        "requests": 0,
        "window_start": datetime.utcnow(),
        "remaining": RATE_LIMIT_MAX_REQUESTS
    }

@app.get("/api/v1/address/{address}")
async def get_address_info(address: str, api_key: str = Depends(check_api_key)):
    """Get address details including balance and transactions."""
    try:
        # Implementation will connect to blockchain node
        info = {}  # Get address info from blockchain
        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address not found: {str(e)}"
        )

@app.get("/api/v1/contract/{address}")
async def get_contract(address: str, api_key: str = Depends(check_api_key)):
    """Get smart contract details."""
    try:
        # Implementation will connect to blockchain node
        contract = {}  # Get contract from blockchain
        return JSONResponse(content=contract)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract not found: {str(e)}"
        )

@app.post("/api/v1/contract/deploy")
async def deploy_contract(contract: Dict, api_key: str = Depends(check_api_key)):
    """Deploy a new smart contract."""
    try:
        # Implementation will connect to blockchain node
        result = {}  # Deploy contract to blockchain
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract deployment failed: {str(e)}"
        )

# Validator Routes
@app.get("/api/v1/validators")
async def get_validators(api_key: str = Depends(check_api_key)):
    """Get list of validators and their stats."""
    try:
        validators = []  # Get validators from blockchain
        return JSONResponse(content=validators)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validators: {str(e)}"
        ) 