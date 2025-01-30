"""
Data models for the API service using Pydantic.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Models
class UserBase(BaseModel):
    email: EmailStr
    two_factor_enabled: bool = False

class UserCreate(UserBase):
    password: str
    confirm_password: str

class User(UserBase):
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"

# Token Models
class TokenCreate(BaseModel):
    name: str
    symbol: str
    description: str
    initial_supply: str
    decimals: int = Field(default=18, ge=0, le=18)
    is_mintable: bool = True
    is_burnable: bool = True
    is_pausable: bool = True
    metadata: Optional[Dict[str, Any]] = None

class Token(TokenCreate):
    id: str
    owner_address: str
    total_supply: str
    created_at: datetime

# Transaction Models
class TransactionBase(BaseModel):
    from_address: str
    to_address: str
    value: str
    gas_limit: Optional[int] = None
    data: Optional[str] = None

class Transaction(TransactionBase):
    hash: str
    timestamp: datetime
    status: str
    block_number: Optional[int] = None
    gas_used: Optional[int] = None

# Response Models
class ResponseModel(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None 