"""ERC721 NFT contract implementation."""

from typing import Dict, Optional

class Contract:
    """ERC721 NFT contract with metadata support."""
    
    def __init__(self, name: str, symbol: str, base_uri: str):
        """
        Initialize NFT contract.
        
        Args:
            name: Collection name
            symbol: Collection symbol
            base_uri: Base URI for token metadata
        """
        globals()['gas_counter'].charge('STORE', 5)
        self.name = name
        self.symbol = symbol
        self.base_uri = base_uri
        self.owner = globals()['sender']
        self.tokens = {}  # token_id -> owner
        self.token_uris = {}  # token_id -> uri
        self.balances = {}  # owner -> token count
        self.approved = {}  # token_id -> approved address
        self.operators = {}  # owner -> operator -> approved
        self.total_supply = 0
        
    def balance_of(self, owner: str) -> int:
        """Get number of tokens owned by address."""
        globals()['gas_counter'].charge('LOAD')
        return self.balances.get(owner, 0)
        
    def owner_of(self, token_id: int) -> str:
        """Get owner of token."""
        globals()['gas_counter'].charge('LOAD')
        assert token_id in self.tokens, "Token does not exist"
        return self.tokens[token_id]
        
    def token_uri(self, token_id: int) -> str:
        """Get token metadata URI."""
        globals()['gas_counter'].charge('LOAD')
        assert token_id in self.tokens, "Token does not exist"
        return self.token_uris.get(token_id, f"{self.base_uri}/{token_id}")
        
    def approve(self, to: str, token_id: int) -> bool:
        """Approve address to transfer token."""
        globals()['gas_counter'].charge('LOAD', 2)
        assert token_id in self.tokens, "Token does not exist"
        assert self.tokens[token_id] == globals()['sender'], "Not token owner"
        
        globals()['gas_counter'].charge('STORE')
        self.approved[token_id] = to
        return True
        
    def get_approved(self, token_id: int) -> str:
        """Get approved address for token."""
        globals()['gas_counter'].charge('LOAD')
        assert token_id in self.tokens, "Token does not exist"
        return self.approved.get(token_id, "0x0")
        
    def set_approval_for_all(self, operator: str, approved: bool) -> bool:
        """Approve operator for all tokens."""
        globals()['gas_counter'].charge('STORE')
        if globals()['sender'] not in self.operators:
            self.operators[globals()['sender']] = {}
        self.operators[globals()['sender']][operator] = approved
        return True
        
    def is_approved_for_all(self, owner: str, operator: str) -> bool:
        """Check if operator is approved for all tokens."""
        globals()['gas_counter'].charge('LOAD')
        return self.operators.get(owner, {}).get(operator, False)
        
    def transfer_from(self, from_addr: str, to: str, token_id: int) -> bool:
        """Transfer token from address."""
        globals()['gas_counter'].charge('LOAD', 3)
        assert token_id in self.tokens, "Token does not exist"
        assert self.tokens[token_id] == from_addr, "Not token owner"
        assert (globals()['sender'] == from_addr or 
               globals()['sender'] == self.approved.get(token_id) or
               self.operators.get(from_addr, {}).get(globals()['sender'], False)), "Not authorized"
        
        globals()['gas_counter'].charge('STORE', 4)
        # Update balances
        self.balances[from_addr] = self.balances.get(from_addr, 0) - 1
        self.balances[to] = self.balances.get(to, 0) + 1
        
        # Update ownership
        self.tokens[token_id] = to
        
        # Clear approval
        if token_id in self.approved:
            del self.approved[token_id]
            
        return True
        
    def mint(self, to: str, token_id: int, uri: Optional[str] = None) -> bool:
        """Mint new token (only owner)."""
        globals()['gas_counter'].charge('LOAD')
        assert globals()['sender'] == self.owner, "Not contract owner"
        assert token_id not in self.tokens, "Token already exists"
        
        globals()['gas_counter'].charge('STORE', 3)
        self.tokens[token_id] = to
        if uri:
            self.token_uris[token_id] = uri
        self.balances[to] = self.balances.get(to, 0) + 1
        self.total_supply += 1
        return True
        
    def burn(self, token_id: int) -> bool:
        """Burn token (only token owner)."""
        globals()['gas_counter'].charge('LOAD', 2)
        assert token_id in self.tokens, "Token does not exist"
        owner = self.tokens[token_id]
        assert globals()['sender'] == owner, "Not token owner"
        
        globals()['gas_counter'].charge('STORE', 3)
        # Update balances
        self.balances[owner] = self.balances.get(owner, 0) - 1
        
        # Remove token
        del self.tokens[token_id]
        if token_id in self.token_uris:
            del self.token_uris[token_id]
        if token_id in self.approved:
            del self.approved[token_id]
            
        self.total_supply -= 1
        return True 