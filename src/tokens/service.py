"""Token service for managing token operations."""

from typing import Optional, Dict, List
from decimal import Decimal
import logging
from datetime import datetime
from .models import Token, TokenMetadata
from .factory import TokenFactory
from src.auth.models import User

logger = logging.getLogger(__name__)


class TokenService:
    """Service for managing token operations."""
    
    def __init__(self, token_factory: TokenFactory):
        """
        Initialize token service.
        
        Args:
            token_factory: Factory for token creation
        """
        self.token_factory = token_factory
        self.minting_limits: Dict[str, Dict] = {}  # user_id -> {daily_limit, used_today}
        
    async def create_token(
        self,
        user: User,
        name: str,
        symbol: str,
        description: str,
        initial_supply: Decimal,
        decimals: int = 18,
        is_mintable: bool = True,
        is_burnable: bool = False,
        is_pausable: bool = True,
        metadata: Optional[Dict] = None
    ) -> Optional[Token]:
        """
        Create and deploy a new token.
        
        Args:
            user: Token creator
            name: Token name
            symbol: Token symbol
            description: Token description
            initial_supply: Initial token supply
            decimals: Token decimals
            is_mintable: Whether token can be minted
            is_burnable: Whether token can be burned
            is_pausable: Whether token can be paused
            metadata: Additional token metadata
            
        Returns:
            Optional[Token]: Created token if successful
        """
        try:
            # Create token
            token = self.token_factory.create_token(
                name=name,
                symbol=symbol,
                description=description,
                owner_address=user.id,  # Using user ID as address for now
                initial_supply=initial_supply,
                decimals=decimals,
                is_mintable=is_mintable,
                is_burnable=is_burnable,
                is_pausable=is_pausable,
                metadata=metadata
            )
            
            # Deploy token contract
            if not await self.token_factory.deploy_token(token):
                logger.error(f"Failed to deploy token: {symbol}")
                return None
                
            # Set initial minting limits for owner
            self.set_minting_limits(user.id, Decimal('1000000'))  # 1M tokens daily limit
            
            logger.info(f"Token created and deployed: {symbol}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            return None
    
    def set_minting_limits(self, user_id: str, daily_limit: Decimal) -> None:
        """Set daily minting limits for a user."""
        self.minting_limits[user_id] = {
            'daily_limit': daily_limit,
            'used_today': Decimal('0'),
            'last_reset': datetime.utcnow().date()
        }
    
    def check_minting_limits(self, user_id: str, amount: Decimal) -> bool:
        """
        Check if minting amount is within user's limits.
        
        Args:
            user_id: User ID
            amount: Amount to mint
            
        Returns:
            bool: True if within limits
        """
        if user_id not in self.minting_limits:
            return False
            
        limits = self.minting_limits[user_id]
        current_date = datetime.utcnow().date()
        
        # Reset daily usage if it's a new day
        if current_date != limits['last_reset']:
            limits['used_today'] = Decimal('0')
            limits['last_reset'] = current_date
        
        # Check if amount is within remaining limit
        remaining = limits['daily_limit'] - limits['used_today']
        return amount <= remaining
    
    def update_minting_usage(self, user_id: str, amount: Decimal) -> None:
        """Update user's minting usage."""
        if user_id in self.minting_limits:
            limits = self.minting_limits[user_id]
            current_date = datetime.utcnow().date()
            
            if current_date != limits['last_reset']:
                limits['used_today'] = amount
                limits['last_reset'] = current_date
            else:
                limits['used_today'] += amount
    
    async def mint_tokens(
        self,
        user: User,
        token_id: str,
        amount: Decimal,
        to_address: str
    ) -> bool:
        """
        Mint new tokens.
        
        Args:
            user: Token minter
            token_id: Token ID
            amount: Amount to mint
            to_address: Recipient address
            
        Returns:
            bool: True if minting successful
        """
        token = self.token_factory.get_token(token_id)
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
            
        # Check ownership and permissions
        if token.owner_address != user.id:
            logger.error(f"User {user.id} not authorized to mint token {token_id}")
            return False
            
        # Check minting limits
        if not self.check_minting_limits(user.id, amount):
            logger.error(f"Minting amount exceeds daily limit for user {user.id}")
            return False
            
        # Mint tokens
        if not token.mint(amount, to_address):
            logger.error(f"Failed to mint {amount} tokens to {to_address}")
            return False
            
        # Update minting usage
        self.update_minting_usage(user.id, amount)
        
        logger.info(f"Minted {amount} tokens to {to_address}")
        return True
    
    def get_user_tokens(self, user: User) -> List[Token]:
        """Get all tokens owned by user."""
        return list(self.token_factory.list_tokens(user.id).values())
    
    def get_token_info(self, token_id: str) -> Optional[Dict]:
        """Get detailed token information."""
        token = self.token_factory.get_token(token_id)
        if not token:
            return None
            
        return {
            'id': token.id,
            'name': token.metadata.name,
            'symbol': token.metadata.symbol,
            'description': token.metadata.description,
            'owner': token.owner_address,
            'contract_address': token.contract_address,
            'total_supply': str(token.total_supply),
            'circulating_supply': str(token.circulating_supply),
            'decimals': token.decimals,
            'is_mintable': token.is_mintable,
            'is_burnable': token.is_burnable,
            'is_pausable': token.is_pausable,
            'is_frozen': token.is_frozen,
            'created_at': token.created_at.isoformat(),
            'last_minted': token.last_minted.isoformat() if token.last_minted else None,
            'holders_count': len(token.holders),
            'metadata': {
                'website': token.metadata.website,
                'socials': token.metadata.socials,
                'tags': token.metadata.tags,
                'image_url': token.metadata.image_url
            }
        }
    
    async def transfer_tokens(
        self,
        user: User,
        token_id: str,
        amount: Decimal,
        to_address: str
    ) -> bool:
        """
        Transfer tokens to another address.
        
        Args:
            user: Token sender
            token_id: Token ID
            amount: Amount to transfer
            to_address: Recipient address
            
        Returns:
            bool: True if transfer successful
        """
        token = self.token_factory.get_token(token_id)
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
            
        # Check transfer permission
        if not token.check_permission(user.id, 'transfer'):
            logger.error(f"User {user.id} not authorized to transfer token {token_id}")
            return False
            
        # Transfer tokens
        if not token.transfer(user.id, to_address, amount):
            logger.error(f"Failed to transfer {amount} tokens to {to_address}")
            return False
            
        # Record transaction
        token.record_transaction(
            tx_type='transfer',
            from_address=user.id,
            to_address=to_address,
            amount=amount
        )
        
        logger.info(f"Transferred {amount} tokens from {user.id} to {to_address}")
        return True
    
    async def burn_tokens(
        self,
        user: User,
        token_id: str,
        amount: Decimal
    ) -> bool:
        """
        Burn tokens.
        
        Args:
            user: Token burner
            token_id: Token ID
            amount: Amount to burn
            
        Returns:
            bool: True if burning successful
        """
        token = self.token_factory.get_token(token_id)
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
            
        # Check burn permission
        if not token.check_permission(user.id, 'burn'):
            logger.error(f"User {user.id} not authorized to burn token {token_id}")
            return False
            
        # Burn tokens
        if not token.burn(amount, user.id):
            logger.error(f"Failed to burn {amount} tokens from {user.id}")
            return False
            
        # Record transaction
        token.record_transaction(
            tx_type='burn',
            from_address=user.id,
            to_address=None,
            amount=amount
        )
        
        logger.info(f"Burned {amount} tokens from {user.id}")
        return True
    
    async def manage_permissions(
        self,
        user: User,
        token_id: str,
        target_address: str,
        permission_type: str,
        grant: bool
    ) -> bool:
        """
        Manage token permissions.
        
        Args:
            user: Permission manager
            token_id: Token ID
            target_address: Address to grant/revoke permission
            permission_type: Type of permission
            grant: True to grant, False to revoke
            
        Returns:
            bool: True if permission updated successfully
        """
        token = self.token_factory.get_token(token_id)
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
            
        # Check admin permission
        if not token.check_permission(user.id, 'admin') and user.id != token.owner_address:
            logger.error(f"User {user.id} not authorized to manage permissions for token {token_id}")
            return False
            
        # Update permission
        if grant:
            success = token.grant_permission(target_address, permission_type)
        else:
            success = token.revoke_permission(target_address, permission_type)
            
        if success:
            action = "granted" if grant else "revoked"
            logger.info(f"{permission_type} permission {action} for {target_address} on token {token_id}")
            
        return success
    
    async def get_token_analytics(self, token_id: str) -> Optional[Dict]:
        """
        Get token analytics.
        
        Args:
            token_id: Token ID
            
        Returns:
            Optional[Dict]: Analytics data if token exists
        """
        token = self.token_factory.get_token(token_id)
        if not token:
            logger.error(f"Token not found: {token_id}")
            return None
            
        return token.get_analytics() 