"""Token factory for creating and deploying tokens."""

from typing import Optional, Dict, List
from decimal import Decimal
import logging
from datetime import datetime
from .models import Token, TokenMetadata
from src.blockchain.smart_contracts.token import Contract as TokenContract
from src.blockchain.smart_contracts.price_oracle import PriceOracle
from src.blockchain.smart_contracts.governance import GovernanceContract
from src.blockchain.smart_contracts.token_swap import TokenSwap
from src.blockchain.smart_contracts.token_vesting import TokenVesting

logger = logging.getLogger(__name__)


class TokenFactory:
    """Factory for creating and managing tokens."""
    
    def __init__(self, blockchain_client):
        """Initialize token factory."""
        self.tokens = {}  # token_id -> Token
        self.blockchain_client = blockchain_client
        self.price_oracle = None
        self.token_swap = None
        
    async def initialize(self):
        """Initialize factory contracts."""
        # Deploy price oracle
        self.price_oracle = PriceOracle()
        self.price_oracle_address = await self.blockchain_client.deploy_contract(
            contract_code=self.price_oracle.__class__.__name__,
            constructor_args=[],
            sender=self.blockchain_client.owner_address
        )
        
        # Deploy token swap
        self.token_swap = TokenSwap()
        self.token_swap_address = await self.blockchain_client.deploy_contract(
            contract_code=self.token_swap.__class__.__name__,
            constructor_args=[],
            sender=self.blockchain_client.owner_address
        )
        
    def create_token(
        self,
        name: str,
        symbol: str,
        description: str,
        owner_address: str,
        initial_supply: Decimal,
        decimals: int = 18,
        is_mintable: bool = True,
        is_burnable: bool = False,
        is_pausable: bool = True,
        enable_governance: bool = False,
        enable_vesting: bool = False,
        metadata: Optional[Dict] = None
    ) -> Token:
        """Create a new token."""
        # Create token metadata
        token_metadata = TokenMetadata(
            name=name,
            symbol=symbol,
            description=description,
            **(metadata or {})
        )
        
        # Create token
        token = Token(
            metadata=token_metadata,
            owner_address=owner_address,
            decimals=decimals,
            is_mintable=is_mintable,
            is_burnable=is_burnable,
            is_pausable=is_pausable
        )
        
        # Mint initial supply
        if initial_supply > 0:
            token.mint(initial_supply, owner_address)
        
        self.tokens[token.id] = token
        
        # Deploy governance contract if enabled
        if enable_governance:
            governance = GovernanceContract(token.contract_address)
            token.governance_address = self.blockchain_client.deploy_contract(
                contract_code=governance.__class__.__name__,
                constructor_args=[token.contract_address],
                sender=owner_address
            )
            
        # Deploy vesting contract if enabled
        if enable_vesting:
            vesting = TokenVesting(token.contract_address)
            token.vesting_address = self.blockchain_client.deploy_contract(
                contract_code=vesting.__class__.__name__,
                constructor_args=[token.contract_address],
                sender=owner_address
            )
            
        logger.info(f"Token created: {name} ({symbol})")
        return token
        
    async def deploy_token(self, token: Token) -> bool:
        """Deploy token contract to blockchain."""
        try:
            # Create contract instance
            contract = TokenContract(
                name=token.metadata.name,
                symbol=token.metadata.symbol,
                total_supply=float(token.total_supply)
            )
            
            # Deploy contract
            contract_address = await self.blockchain_client.deploy_contract(
                contract_code=contract.__class__.__name__,
                constructor_args=[
                    token.metadata.name,
                    token.metadata.symbol,
                    float(token.total_supply)
                ],
                sender=token.owner_address
            )
            
            if not contract_address:
                logger.error(f"Failed to deploy token contract: {token.metadata.symbol}")
                return False
            
            # Update token with contract address
            token.contract_address = contract_address
            token.updated_at = datetime.utcnow()
            
            # Create liquidity pool if token swap exists
            if self.token_swap:
                self.token_swap.create_pool(
                    token_address=contract_address,
                    quote_token=self.blockchain_client.native_token_address
                )
            
            logger.info(f"Token deployed: {token.metadata.symbol} at {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying token contract: {str(e)}")
            return False
            
    def get_token(self, token_id: str) -> Optional[Token]:
        """Get token by ID."""
        return self.tokens.get(token_id)
        
    def get_token_by_symbol(self, symbol: str) -> Optional[Token]:
        """Get token by symbol."""
        for token in self.tokens.values():
            if token.metadata.symbol.upper() == symbol.upper():
                return token
        return None
        
    def get_token_by_contract(self, contract_address: str) -> Optional[Token]:
        """Get token by contract address."""
        for token in self.tokens.values():
            if token.contract_address == contract_address:
                return token
        return None
        
    def list_tokens(self, owner_address: Optional[str] = None) -> Dict[str, Token]:
        """List all tokens or tokens owned by address."""
        if not owner_address:
            return self.tokens
            
        return {
            token_id: token
            for token_id, token in self.tokens.items()
            if token.owner_address == owner_address
        }
        
    def get_token_price(self, token_id: str) -> float:
        """Get token price from oracle."""
        if not self.price_oracle:
            return 0
            
        token = self.get_token(token_id)
        if not token:
            return 0
            
        price_data = self.price_oracle.get_price(token.contract_address)
        return price_data.get('price', 0)
        
    def get_token_pools(self, token_id: str) -> List[Dict]:
        """Get liquidity pools for token."""
        if not self.token_swap:
            return []
            
        token = self.get_token(token_id)
        if not token:
            return []
            
        pools = []
        for quote_token in self.tokens.values():
            if quote_token.id != token_id:
                pool_info = self.token_swap.get_pool_info(
                    token.contract_address,
                    quote_token.contract_address
                )
                if pool_info:
                    pools.append(pool_info)
                    
        return pools 