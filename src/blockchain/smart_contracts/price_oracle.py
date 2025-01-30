"""Price oracle contract for token price tracking."""

class PriceOracle:
    """Oracle contract for tracking token prices."""
    
    def __init__(self):
        """Initialize the price oracle."""
        self.prices = {}  # token_address -> {price, timestamp, provider}
        self.providers = {}  # provider_address -> is_authorized
        self.owner = globals()['sender']
        
    def update_price(self, token_address: str, price: float) -> bool:
        """
        Update token price (only authorized providers).
        
        Args:
            token_address: Token contract address
            price: New price in USD
            
        Returns:
            bool: True if price update successful
        """
        if not self.providers.get(globals()['sender'], False):
            return False
            
        self.prices[token_address] = {
            'price': price,
            'timestamp': globals()['block_timestamp'],
            'provider': globals()['sender']
        }
        return True
        
    def get_price(self, token_address: str) -> dict:
        """
        Get latest price data for a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            dict: Price data including timestamp and provider
        """
        return self.prices.get(token_address, {
            'price': 0.0,
            'timestamp': 0,
            'provider': None
        })
        
    def add_provider(self, provider_address: str) -> bool:
        """Add authorized price provider (only owner)."""
        if globals()['sender'] != self.owner:
            return False
            
        self.providers[provider_address] = True
        return True
        
    def remove_provider(self, provider_address: str) -> bool:
        """Remove authorized price provider (only owner)."""
        if globals()['sender'] != self.owner:
            return False
            
        self.providers.pop(provider_address, None)
        return True 