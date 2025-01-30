"""Token swap contract for enabling token swapping functionality."""

from typing import Dict, Optional

class LiquidityPool:
    def __init__(self, token_a: str, token_b: str):
        self.token_a = token_a
        self.token_b = token_b
        self.reserve_a = 0.0
        self.reserve_b = 0.0
        self.total_shares = 0.0
        self.shares = {}  # address -> LP token amount
        self.fee_rate = 0.003  # 0.3% fee
        
class TokenSwap:
    """Contract for token swapping and liquidity provision."""
    
    def __init__(self):
        """Initialize the token swap contract."""
        self.pools = {}  # (token_a, token_b) -> LiquidityPool
        self.owner = globals()['sender']
        
    def create_pool(self, token_a: str, token_b: str) -> bool:
        """
        Create a new liquidity pool.
        
        Args:
            token_a: First token address
            token_b: Second token address
            
        Returns:
            bool: True if pool creation successful
        """
        # Ensure tokens are different and ordered
        if token_a >= token_b:
            token_a, token_b = token_b, token_a
            
        # Check if pool already exists
        if (token_a, token_b) in self.pools:
            return False
            
        self.pools[(token_a, token_b)] = LiquidityPool(token_a, token_b)
        return True
        
    def add_liquidity(self, token_a: str, token_b: str, amount_a: float, amount_b: float,
                     min_shares: float = 0) -> bool:
        """
        Add liquidity to pool.
        
        Args:
            token_a: First token address
            token_b: Second token address
            amount_a: Amount of first token
            amount_b: Amount of second token
            min_shares: Minimum shares to receive
            
        Returns:
            bool: True if liquidity addition successful
        """
        # Get ordered tokens and pool
        if token_a >= token_b:
            token_a, token_b = token_b, token_a
            amount_a, amount_b = amount_b, amount_a
            
        pool = self.pools.get((token_a, token_b))
        if not pool:
            return False
            
        # Transfer tokens to pool
        token_a_contract = globals()['contracts'][token_a]
        token_b_contract = globals()['contracts'][token_b]
        
        if not (token_a_contract.transfer_from(globals()['sender'], globals()['contract_address'], amount_a) and
                token_b_contract.transfer_from(globals()['sender'], globals()['contract_address'], amount_b)):
            return False
            
        # Calculate shares
        if pool.total_shares == 0:
            shares = (amount_a * amount_b) ** 0.5
        else:
            shares = min(
                amount_a * pool.total_shares / pool.reserve_a,
                amount_b * pool.total_shares / pool.reserve_b
            )
            
        if shares < min_shares:
            return False
            
        # Update pool state
        pool.reserve_a += amount_a
        pool.reserve_b += amount_b
        pool.total_shares += shares
        pool.shares[globals()['sender']] = pool.shares.get(globals()['sender'], 0) + shares
        
        return True
        
    def remove_liquidity(self, token_a: str, token_b: str, shares: float,
                        min_amount_a: float = 0, min_amount_b: float = 0) -> bool:
        """
        Remove liquidity from pool.
        
        Args:
            token_a: First token address
            token_b: Second token address
            shares: Amount of shares to burn
            min_amount_a: Minimum amount of first token
            min_amount_b: Minimum amount of second token
            
        Returns:
            bool: True if liquidity removal successful
        """
        # Get ordered tokens and pool
        if token_a >= token_b:
            token_a, token_b = token_b, token_a
            min_amount_a, min_amount_b = min_amount_b, min_amount_a
            
        pool = self.pools.get((token_a, token_b))
        if not pool:
            return False
            
        # Check user's shares
        user_shares = pool.shares.get(globals()['sender'], 0)
        if user_shares < shares:
            return False
            
        # Calculate token amounts
        amount_a = shares * pool.reserve_a / pool.total_shares
        amount_b = shares * pool.reserve_b / pool.total_shares
        
        if amount_a < min_amount_a or amount_b < min_amount_b:
            return False
            
        # Transfer tokens back to user
        token_a_contract = globals()['contracts'][token_a]
        token_b_contract = globals()['contracts'][token_b]
        
        if not (token_a_contract.transfer(globals()['sender'], amount_a) and
                token_b_contract.transfer(globals()['sender'], amount_b)):
            return False
            
        # Update pool state
        pool.reserve_a -= amount_a
        pool.reserve_b -= amount_b
        pool.total_shares -= shares
        pool.shares[globals()['sender']] -= shares
        
        return True
        
    def swap(self, token_in: str, token_out: str, amount_in: float,
             min_amount_out: float = 0) -> float:
        """
        Swap tokens.
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount
            min_amount_out: Minimum output amount
            
        Returns:
            float: Output amount
        """
        # Get ordered tokens and pool
        reverse = token_in > token_out
        if reverse:
            token_in, token_out = token_out, token_in
            
        pool = self.pools.get((token_in, token_out))
        if not pool:
            return 0
            
        # Calculate output amount using constant product formula
        if reverse:
            reserve_in = pool.reserve_b
            reserve_out = pool.reserve_a
        else:
            reserve_in = pool.reserve_a
            reserve_out = pool.reserve_b
            
        amount_in_with_fee = amount_in * (1 - pool.fee_rate)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
        
        if amount_out < min_amount_out:
            return 0
            
        # Transfer tokens
        token_in_contract = globals()['contracts'][token_in]
        token_out_contract = globals()['contracts'][token_out]
        
        if not token_in_contract.transfer_from(globals()['sender'], globals()['contract_address'], amount_in):
            return 0
            
        if not token_out_contract.transfer(globals()['sender'], amount_out):
            return 0
            
        # Update pool state
        if reverse:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out
        else:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
            
        return amount_out
        
    def get_pool_info(self, token_a: str, token_b: str) -> Dict:
        """Get pool information."""
        if token_a >= token_b:
            token_a, token_b = token_b, token_a
            
        pool = self.pools.get((token_a, token_b))
        if not pool:
            return {}
            
        return {
            'token_a': pool.token_a,
            'token_b': pool.token_b,
            'reserve_a': pool.reserve_a,
            'reserve_b': pool.reserve_b,
            'total_shares': pool.total_shares,
            'fee_rate': pool.fee_rate
        }
        
    def get_swap_amount_out(self, token_in: str, token_out: str, amount_in: float) -> float:
        """Calculate output amount for a swap."""
        reverse = token_in > token_out
        if reverse:
            token_in, token_out = token_out, token_in
            
        pool = self.pools.get((token_in, token_out))
        if not pool:
            return 0
            
        if reverse:
            reserve_in = pool.reserve_b
            reserve_out = pool.reserve_a
        else:
            reserve_in = pool.reserve_a
            reserve_out = pool.reserve_b
            
        amount_in_with_fee = amount_in * (1 - pool.fee_rate)
        return (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee) 