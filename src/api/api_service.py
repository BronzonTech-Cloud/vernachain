"""
API Service for Vernachain.

This module provides RESTful API endpoints for blockchain interaction.
"""

from fastapi import FastAPI, Depends, HTTPException, Security, status, Request, Response
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from pydantic import BaseModel, Field, EmailStr
import os
import secrets
from src.auth import AuthService, User 
from decimal import Decimal
from src.tokens import TokenService, TokenFactory
from src.blockchain.client import BlockchainClient

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

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class Enable2FARequest(BaseModel):
    password: str

class Verify2FARequest(BaseModel):
    code: str

# Add new token models
class TokenTransferRequest(BaseModel):
    token_id: str = Field(..., description="Token ID")
    to_address: str = Field(..., description="Recipient address")
    amount: str = Field(..., description="Amount to transfer")

class TokenBurnRequest(BaseModel):
    token_id: str = Field(..., description="Token ID")
    amount: str = Field(..., description="Amount to burn")

class TokenPermissionRequest(BaseModel):
    token_id: str = Field(..., description="Token ID")
    address: str = Field(..., description="Address to grant/revoke permissions")
    permission_type: str = Field(..., description="Permission type (mint, burn, transfer, admin)")
    grant: bool = Field(..., description="True to grant, False to revoke")

# Initialize FastAPI and Auth Service
app = FastAPI(
    title="Vernachain API",
    description="Official API for Vernachain blockchain",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize auth service with secret key
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
auth_service = AuthService(secret_key=SECRET_KEY)

# Initialize services
blockchain_client = BlockchainClient()
token_factory = TokenFactory(blockchain_client)
token_service = TokenService(token_factory)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Authorization"],
    expose_headers=["Set-Cookie"]
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

# Custom exceptions
class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message: str, fields: Optional[Dict[str, str]] = None):
        self.message = message
        self.fields = fields or {}
        super().__init__(self.message)

# Exception handlers
@app.exception_handler(AuthError)
async def auth_exception_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Authentication error",
            "message": exc.message
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": exc.message,
            "fields": exc.fields
        }
    )

# Authentication Routes
@app.post("/api/v1/auth/register")
async def register(request: UserRegisterRequest):
    """Register a new user."""
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    try:
        user = auth_service.register_user(request.email, request.password)
        return {
            "message": "Registration successful",
            "user_id": user.id,
            "email": user.email
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/v1/auth/login")
async def login(request: UserLoginRequest, response: Response):
    try:
        session = auth_service.login(request.email, request.password)
        if not session:
            raise AuthError("Invalid credentials")
        
        response.set_cookie(
            key="session",
            value=session,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=datetime.now() + timedelta(days=7)
        )
        return {"status": "success", "email": request.email}
    except AuthError as e:
        raise
    except Exception as e:
        raise AuthError(f"Login failed: {str(e)}")

async def get_current_session(request: Request) -> str:
    """Get current session from cookie."""
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return session

@app.post("/api/v1/auth/logout")
async def logout(response: Response, session: str = Depends(get_current_session)):
    try:
        auth_service.logout(session)
        response.delete_cookie(key="session")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_current_user(
    session: str = Depends(get_current_session)
) -> User:
    """Get current user from session."""
    user = auth_service.verify_session(session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return user 

@app.post("/api/v1/auth/enable-2fa")
async def enable_2fa(
    request: Enable2FARequest,
    user: User = Depends(get_current_user)
):
    """Enable 2FA for user."""
    # Verify password before enabling 2FA
    if not auth_service.verify_password(user.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    secret = user.enable_2fa()
    return {
        "secret": secret,
        "qr_code": f"otpauth://totp/Vernachain:{user.email}?secret={secret}&issuer=Vernachain"
    }

@app.post("/api/v1/auth/verify-2fa")
async def verify_2fa(
    request: Verify2FARequest,
    user: User = Depends(get_current_user)
):
    """Verify 2FA setup."""
    if not user.verify_2fa(request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    return {"message": "2FA verified successfully"}

@app.post("/api/v1/auth/disable-2fa")
async def disable_2fa(
    request: Enable2FARequest,
    user: User = Depends(get_current_user)
):
    """Disable 2FA for user."""
    # Verify password before disabling 2FA
    if not auth_service.verify_password(user.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    user.disable_2fa()
    return {"message": "2FA disabled successfully"}

@app.post("/api/v1/auth/reset-password")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset token."""
    token = auth_service.generate_password_reset_token(request.email)
    if token:
        # In production, send this token via email
        return {
            "message": "Password reset instructions sent",
            "token": token  # Remove in production
        }
    return {"message": "Password reset instructions sent"}

@app.post("/api/v1/auth/reset-password/confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest):
    """Reset password using token."""
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if auth_service.reset_password(request.token, request.new_password):
        return {"message": "Password reset successful"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token"
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

# Token Models
class CreateTokenRequest(BaseModel):
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    description: str = Field(..., description="Token description")
    initial_supply: str = Field(..., description="Initial token supply")
    decimals: int = Field(default=18, description="Token decimals")
    is_mintable: bool = Field(default=True, description="Whether token can be minted")
    is_burnable: bool = Field(default=False, description="Whether token can be burned")
    is_pausable: bool = Field(default=True, description="Whether token can be paused")
    metadata: Optional[Dict] = Field(default=None, description="Additional token metadata")

class MintTokenRequest(BaseModel):
    token_id: str = Field(..., description="Token ID")
    amount: str = Field(..., description="Amount to mint")
    to_address: str = Field(..., description="Recipient address")

# Token Routes
@app.post("/api/v1/tokens/create")
async def create_token(
    request: CreateTokenRequest,
    user: User = Depends(get_current_user)
):
    """Create a new token."""
    try:
        initial_supply = Decimal(request.initial_supply)
        token = await token_service.create_token(
            user=user,
            name=request.name,
            symbol=request.symbol,
            description=request.description,
            initial_supply=initial_supply,
            decimals=request.decimals,
            is_mintable=request.is_mintable,
            is_burnable=request.is_burnable,
            is_pausable=request.is_pausable,
            metadata=request.metadata
        )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create token"
            )
            
        return {
            "message": "Token created successfully",
            "token_id": token.id,
            "contract_address": token.contract_address
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/v1/tokens/mint")
async def mint_tokens(
    request: MintTokenRequest,
    user: User = Depends(get_current_user)
):
    """Mint new tokens."""
    try:
        amount = Decimal(request.amount)
        if await token_service.mint_tokens(
            user=user,
            token_id=request.token_id,
            amount=amount,
            to_address=request.to_address
        ):
            return {"message": "Tokens minted successfully"}
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to mint tokens"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/v1/tokens")
async def list_tokens(user: User = Depends(get_current_user)):
    """List user's tokens."""
    tokens = token_service.get_user_tokens(user)
    return {
        "tokens": [token_service.get_token_info(token.id) for token in tokens]
    }

@app.get("/api/v1/tokens/{token_id}")
async def get_token(
    token_id: str,
    user: User = Depends(get_current_user)
):
    """Get token details."""
    token_info = token_service.get_token_info(token_id)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    return token_info

# Add new token endpoints
@app.post("/api/v1/tokens/transfer")
async def transfer_tokens(
    request: TokenTransferRequest,
    user: User = Depends(get_current_user)
):
    """Transfer tokens to another address."""
    try:
        amount = Decimal(request.amount)
        if await token_service.transfer_tokens(
            user=user,
            token_id=request.token_id,
            amount=amount,
            to_address=request.to_address
        ):
            return {"message": "Tokens transferred successfully"}
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to transfer tokens"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/v1/tokens/burn")
async def burn_tokens(
    request: TokenBurnRequest,
    user: User = Depends(get_current_user)
):
    """Burn tokens."""
    try:
        amount = Decimal(request.amount)
        if await token_service.burn_tokens(
            user=user,
            token_id=request.token_id,
            amount=amount
        ):
            return {"message": "Tokens burned successfully"}
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to burn tokens"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/v1/tokens/{token_id}/permissions")
async def manage_token_permissions(
    token_id: str,
    request: TokenPermissionRequest,
    user: User = Depends(get_current_user)
):
    """Manage token permissions."""
    try:
        if await token_service.manage_permissions(
            user=user,
            token_id=token_id,
            target_address=request.address,
            permission_type=request.permission_type,
            grant=request.grant
        ):
            action = "granted" if request.grant else "revoked"
            return {
                "message": f"Permission {action} successfully"
            }
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to manage permissions"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/v1/tokens/{token_id}/analytics")
async def get_token_analytics(
    token_id: str,
    user: User = Depends(get_current_user)
):
    """Get token analytics."""
    analytics = await token_service.get_token_analytics(token_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    return analytics

# Dependencies
async def get_current_session(request: Request) -> str:
    """Get current session from cookie."""
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return session

async def get_current_user(
    session: str = Depends(get_current_session)
) -> User:
    """Get current user from session."""
    user = auth_service.verify_session(session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return user 