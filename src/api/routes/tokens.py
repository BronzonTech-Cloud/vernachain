"""
Token management routes for the API service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ..models import TokenCreate, Token, ResponseModel, User
from ..middleware.auth import get_current_user
from ..database import get_db, DBToken, DBTransaction, DBTokenHolder, TransactionStatus
from ..blockchain.client import BlockchainClient
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

router = APIRouter()
blockchain = BlockchainClient()

@router.post("/create", response_model=ResponseModel)
async def create_token(
    token: TokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """Create a new token"""
    try:
        # Create token transaction
        tx = blockchain.create_token({
            "name": token.name,
            "symbol": token.symbol,
            "initial_supply": token.initial_supply,
            "decimals": token.decimals,
            "is_mintable": token.is_mintable,
            "is_burnable": token.is_burnable,
            "is_pausable": token.is_pausable,
            "owner_address": current_user.wallet_address
        })
        
        # Save token to database
        db_token = DBToken(
            id=str(uuid.uuid4()),
            name=token.name,
            symbol=token.symbol,
            description=token.description,
            owner_id=current_user.id,
            total_supply=token.initial_supply,
            decimals=token.decimals,
            is_mintable=token.is_mintable,
            is_burnable=token.is_burnable,
            is_pausable=token.is_pausable,
            deployment_tx_hash=tx["hash"]
        )
        db.add(db_token)
        
        # Save transaction
        db_tx = DBTransaction(
            id=str(uuid.uuid4()),
            tx_hash=tx["hash"],
            user_id=current_user.id,
            token_id=db_token.id,
            from_address="0x0000000000000000000000000000000000000000",
            to_address=current_user.wallet_address,
            amount=token.initial_supply,
            gas_price=str(tx["gasPrice"]),
            status=TransactionStatus.PENDING,
            type="create"
        )
        db.add(db_tx)
        db.commit()

        return ResponseModel(
            success=True,
            data={"token": db_token},
            message="Token creation transaction submitted"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/list", response_model=ResponseModel)
async def list_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """List all tokens"""
    try:
        tokens = db.query(DBToken).filter(DBToken.owner_id == current_user.id).all()
        return ResponseModel(
            success=True,
            data={"tokens": tokens},
            message="Tokens retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{token_id}", response_model=ResponseModel)
async def get_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """Get token details"""
    try:
        token = db.query(DBToken).filter(
            DBToken.id == token_id,
            DBToken.owner_id == current_user.id
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
            
        # Get on-chain data
        if token.contract_address:
            chain_info = blockchain.get_token_info(token.contract_address)
            token.total_supply = chain_info["total_supply"]
            db.commit()
            
        return ResponseModel(
            success=True,
            data={"token": token},
            message="Token retrieved successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/transfer", response_model=ResponseModel)
async def transfer_tokens(
    token_id: str,
    to_address: str,
    amount: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """Transfer tokens"""
    try:
        token = db.query(DBToken).filter(
            DBToken.id == token_id,
            DBToken.owner_id == current_user.id
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
            
        # Create transfer transaction
        tx = blockchain.transfer_tokens(
            token.contract_address,
            current_user.wallet_address,
            to_address,
            amount
        )
        
        # Save transaction
        db_tx = DBTransaction(
            id=str(uuid.uuid4()),
            tx_hash=tx["hash"],
            user_id=current_user.id,
            token_id=token.id,
            from_address=current_user.wallet_address,
            to_address=to_address,
            amount=amount,
            gas_price=str(tx["gasPrice"]),
            status=TransactionStatus.PENDING,
            type="transfer"
        )
        db.add(db_tx)
        db.commit()

        return ResponseModel(
            success=True,
            data={"transaction": db_tx},
            message="Transfer transaction submitted"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/mint", response_model=ResponseModel)
async def mint_tokens(
    token_id: str,
    amount: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """Mint new tokens"""
    try:
        token = db.query(DBToken).filter(
            DBToken.id == token_id,
            DBToken.owner_id == current_user.id
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
            
        if not token.is_mintable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is not mintable"
            )
            
        # Create mint transaction
        tx = blockchain.mint_tokens(
            token.contract_address,
            current_user.wallet_address,
            amount,
            current_user.wallet_address
        )
        
        # Save transaction
        db_tx = DBTransaction(
            id=str(uuid.uuid4()),
            tx_hash=tx["hash"],
            user_id=current_user.id,
            token_id=token.id,
            from_address="0x0000000000000000000000000000000000000000",
            to_address=current_user.wallet_address,
            amount=amount,
            gas_price=str(tx["gasPrice"]),
            status=TransactionStatus.PENDING,
            type="mint"
        )
        db.add(db_tx)
        db.commit()

        return ResponseModel(
            success=True,
            data={"transaction": db_tx},
            message="Mint transaction submitted"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/burn", response_model=ResponseModel)
async def burn_tokens(
    token_id: str,
    amount: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseModel:
    """Burn tokens"""
    try:
        token = db.query(DBToken).filter(
            DBToken.id == token_id,
            DBToken.owner_id == current_user.id
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
            
        if not token.is_burnable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is not burnable"
            )
            
        # Create burn transaction
        tx = blockchain.burn_tokens(
            token.contract_address,
            amount,
            current_user.wallet_address
        )
        
        # Save transaction
        db_tx = DBTransaction(
            id=str(uuid.uuid4()),
            tx_hash=tx["hash"],
            user_id=current_user.id,
            token_id=token.id,
            from_address=current_user.wallet_address,
            to_address="0x0000000000000000000000000000000000000000",
            amount=amount,
            gas_price=str(tx["gasPrice"]),
            status=TransactionStatus.PENDING,
            type="burn"
        )
        db.add(db_tx)
        db.commit()

        return ResponseModel(
            success=True,
            data={"transaction": db_tx},
            message="Burn transaction submitted"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 