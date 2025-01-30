"""
Database integration for the API service.
"""

from sqlalchemy import create_engine, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Text
import os
from datetime import datetime
import enum

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./vernachain.db"  # SQLite as fallback
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

class TransactionStatus(enum.Enum):
    """Transaction status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class TokenType(enum.Enum):
    """Token type enum"""
    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"

# Database Models
class DBUser(Base):
    """User database model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    wallet_address = Column(String, unique=True, index=True)
    wallet_private_key = Column(String)  # Encrypted
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    nonce = Column(String, unique=True)  # For wallet signature authentication
    
    # Relationships
    tokens = relationship("DBToken", back_populates="owner")
    transactions = relationship("DBTransaction", back_populates="user")

class DBToken(Base):
    """Token database model"""
    __tablename__ = "tokens"

    id = Column(String, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    description = Column(String)
    owner_id = Column(String, ForeignKey("users.id"))
    contract_address = Column(String, unique=True, index=True)
    total_supply = Column(String)
    decimals = Column(Integer)
    token_type = Column(Enum(TokenType))
    metadata_uri = Column(String, nullable=True)
    is_mintable = Column(Boolean)
    is_burnable = Column(Boolean)
    is_pausable = Column(Boolean)
    is_paused = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deployment_tx_hash = Column(String)
    contract_abi = Column(JSON)
    
    # Relationships
    owner = relationship("DBUser", back_populates="tokens")
    transactions = relationship("DBTransaction", back_populates="token")
    holders = relationship("DBTokenHolder", back_populates="token")

class DBTransaction(Base):
    """Transaction database model"""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    tx_hash = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    token_id = Column(String, ForeignKey("tokens.id"))
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    amount = Column(String)
    gas_price = Column(String)
    gas_used = Column(String, nullable=True)
    status = Column(Enum(TransactionStatus))
    type = Column(String)  # transfer, mint, burn, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    block_number = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("DBUser", back_populates="transactions")
    token = relationship("DBToken", back_populates="transactions")

class DBTokenHolder(Base):
    """Token holder database model"""
    __tablename__ = "token_holders"

    id = Column(String, primary_key=True)
    token_id = Column(String, ForeignKey("tokens.id"))
    holder_address = Column(String, index=True)
    balance = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    token = relationship("DBToken", back_populates="holders")

# Database dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine) 