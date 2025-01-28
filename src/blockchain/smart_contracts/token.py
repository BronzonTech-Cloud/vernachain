class Contract:
    """Template for ERC20-like token contracts."""
    
    def __init__(self, name: str, symbol: str, total_supply: float):
        """
        Initialize the token contract.
        
        Args:
            name: Token name
            symbol: Token symbol
            total_supply: Initial total supply
        """
        # Access gas_counter from globals
        globals()['gas_counter'].charge('STORE', 4)
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.balances = {globals()['sender']: total_supply}
        self.allowances = {}
        
    def balance_of(self, address: str) -> float:
        """
        Get the token balance of an address.
        
        Args:
            address: Address to check
            
        Returns:
            float: Token balance
        """
        globals()['gas_counter'].charge('LOAD')
        return self.balances.get(address, 0.0)
        
    def transfer(self, to: str, amount: float) -> bool:
        """
        Transfer tokens to another address.
        
        Args:
            to: Recipient address
            amount: Amount to transfer
            
        Returns:
            bool: True if transfer successful
        """
        globals()['gas_counter'].charge('LOAD', 2)
        if self.balances.get(globals()['sender'], 0.0) < amount:
            return False
            
        globals()['gas_counter'].charge('STORE', 2)
        self.balances[globals()['sender']] = self.balances.get(globals()['sender'], 0.0) - amount
        self.balances[to] = self.balances.get(to, 0.0) + amount
        return True
        
    def approve(self, spender: str, amount: float) -> bool:
        """
        Approve an address to spend tokens.
        
        Args:
            spender: Address to approve
            amount: Amount to approve
            
        Returns:
            bool: True if approval successful
        """
        globals()['gas_counter'].charge('STORE')
        if globals()['sender'] not in self.allowances:
            self.allowances[globals()['sender']] = {}
            
        self.allowances[globals()['sender']][spender] = amount
        return True
        
    def allowance(self, owner: str, spender: str) -> float:
        """
        Get the amount of tokens approved for spending.
        
        Args:
            owner: Token owner's address
            spender: Spender's address
            
        Returns:
            float: Approved amount
        """
        globals()['gas_counter'].charge('LOAD')
        return self.allowances.get(owner, {}).get(spender, 0.0)
        
    def transfer_from(self, from_addr: str, to: str, amount: float) -> bool:
        """
        Transfer tokens on behalf of another address.
        
        Args:
            from_addr: Token owner's address
            to: Recipient address
            amount: Amount to transfer
            
        Returns:
            bool: True if transfer successful
        """
        globals()['gas_counter'].charge('LOAD', 3)
        allowed = self.allowances.get(from_addr, {}).get(globals()['sender'], 0.0)
        if allowed < amount or self.balances.get(from_addr, 0.0) < amount:
            return False
            
        globals()['gas_counter'].charge('STORE', 3)
        self.balances[from_addr] = self.balances.get(from_addr, 0.0) - amount
        self.balances[to] = self.balances.get(to, 0.0) + amount
        self.allowances[from_addr][globals()['sender']] = allowed - amount
        return True
        
    def mint(self, to: str, amount: float) -> bool:
        """
        Mint new tokens (only contract owner).
        
        Args:
            to: Recipient address
            amount: Amount to mint
            
        Returns:
            bool: True if minting successful
        """
        globals()['gas_counter'].charge('LOAD')
        if globals()['sender'] != globals()['contract_address']:
            return False
            
        globals()['gas_counter'].charge('STORE', 2)
        self.total_supply += amount
        self.balances[to] = self.balances.get(to, 0.0) + amount
        return True
        
    def burn(self, amount: float) -> bool:
        """
        Burn tokens from sender's balance.
        
        Args:
            amount: Amount to burn
            
        Returns:
            bool: True if burning successful
        """
        globals()['gas_counter'].charge('LOAD')
        if self.balances.get(globals()['sender'], 0.0) < amount:
            return False
            
        globals()['gas_counter'].charge('STORE', 2)
        self.total_supply -= amount
        self.balances[globals()['sender']] = self.balances.get(globals()['sender'], 0.0) - amount
        return True 