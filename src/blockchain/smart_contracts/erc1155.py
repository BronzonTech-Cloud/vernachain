"""ERC1155 Multi-Token contract implementation."""

from typing import Dict, List

class Contract:
    """ERC1155 Multi-Token contract with metadata support."""
    
    def __init__(self, name: str, uri: str):
        """
        Initialize Multi-Token contract.
        
        Args:
            name: Collection name
            uri: Metadata URI with {id} placeholder
        """
        globals()['gas_counter'].charge('STORE', 4)
        self.name = name
        self.uri = uri
        self.owner = globals()['sender']
        self.balances = {}  # token_id -> owner -> amount
        self.operators = {}  # owner -> operator -> approved
        self.token_supplies = {}  # token_id -> total supply
        
    def balance_of(self, account: str, token_id: int) -> int:
        """Get token balance of account."""
        globals()['gas_counter'].charge('LOAD', 2)
        return self.balances.get(token_id, {}).get(account, 0)
        
    def balance_of_batch(self, accounts: List[str], token_ids: List[int]) -> List[int]:
        """Get token balances for multiple account/token pairs."""
        globals()['gas_counter'].charge('LOAD', len(accounts))
        assert len(accounts) == len(token_ids), "Array length mismatch"
        return [self.balance_of(account, token_id) 
                for account, token_id in zip(accounts, token_ids)]
        
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
        
    def safe_transfer_from(self, from_addr: str, to: str, token_id: int,
                          amount: int, data: bytes = b'') -> bool:
        """Transfer tokens from address."""
        globals()['gas_counter'].charge('LOAD', 3)
        assert (globals()['sender'] == from_addr or 
               self.operators.get(from_addr, {}).get(globals()['sender'], False)), "Not authorized"
               
        if token_id not in self.balances:
            self.balances[token_id] = {}
            
        current_balance = self.balances[token_id].get(from_addr, 0)
        assert current_balance >= amount, "Insufficient balance"
        
        globals()['gas_counter'].charge('STORE', 2)
        # Update balances
        self.balances[token_id][from_addr] = current_balance - amount
        self.balances[token_id][to] = self.balances[token_id].get(to, 0) + amount
        
        return True
        
    def safe_batch_transfer_from(self, from_addr: str, to: str, token_ids: List[int],
                                amounts: List[int], data: bytes = b'') -> bool:
        """Batch transfer tokens from address."""
        globals()['gas_counter'].charge('LOAD', len(token_ids) * 2)
        assert len(token_ids) == len(amounts), "Array length mismatch"
        assert (globals()['sender'] == from_addr or 
               self.operators.get(from_addr, {}).get(globals()['sender'], False)), "Not authorized"
               
        for token_id, amount in zip(token_ids, amounts):
            if token_id not in self.balances:
                self.balances[token_id] = {}
                
            current_balance = self.balances[token_id].get(from_addr, 0)
            assert current_balance >= amount, f"Insufficient balance for token {token_id}"
            
            # Update balances
            self.balances[token_id][from_addr] = current_balance - amount
            self.balances[token_id][to] = self.balances[token_id].get(to, 0) + amount
            
        return True
        
    def mint(self, to: str, token_id: int, amount: int, data: bytes = b'') -> bool:
        """Mint tokens (only owner)."""
        globals()['gas_counter'].charge('LOAD')
        assert globals()['sender'] == self.owner, "Not contract owner"
        
        globals()['gas_counter'].charge('STORE', 2)
        if token_id not in self.balances:
            self.balances[token_id] = {}
            
        self.balances[token_id][to] = self.balances[token_id].get(to, 0) + amount
        self.token_supplies[token_id] = self.token_supplies.get(token_id, 0) + amount
        return True
        
    def mint_batch(self, to: str, token_ids: List[int], amounts: List[int],
                   data: bytes = b'') -> bool:
        """Batch mint tokens (only owner)."""
        globals()['gas_counter'].charge('LOAD')
        assert globals()['sender'] == self.owner, "Not contract owner"
        assert len(token_ids) == len(amounts), "Array length mismatch"
        
        globals()['gas_counter'].charge('STORE', len(token_ids) * 2)
        for token_id, amount in zip(token_ids, amounts):
            if token_id not in self.balances:
                self.balances[token_id] = {}
                
            self.balances[token_id][to] = self.balances[token_id].get(to, 0) + amount
            self.token_supplies[token_id] = self.token_supplies.get(token_id, 0) + amount
            
        return True
        
    def burn(self, token_id: int, amount: int) -> bool:
        """Burn tokens."""
        globals()['gas_counter'].charge('LOAD', 2)
        current_balance = self.balances.get(token_id, {}).get(globals()['sender'], 0)
        assert current_balance >= amount, "Insufficient balance"
        
        globals()['gas_counter'].charge('STORE', 2)
        self.balances[token_id][globals()['sender']] = current_balance - amount
        self.token_supplies[token_id] -= amount
        return True
        
    def burn_batch(self, token_ids: List[int], amounts: List[int]) -> bool:
        """Batch burn tokens."""
        globals()['gas_counter'].charge('LOAD', len(token_ids))
        assert len(token_ids) == len(amounts), "Array length mismatch"
        
        for token_id, amount in zip(token_ids, amounts):
            current_balance = self.balances.get(token_id, {}).get(globals()['sender'], 0)
            assert current_balance >= amount, f"Insufficient balance for token {token_id}"
            
            self.balances[token_id][globals()['sender']] = current_balance - amount
            self.token_supplies[token_id] -= amount
            
        return True
        
    def uri(self, token_id: int) -> str:
        """Get token metadata URI."""
        globals()['gas_counter'].charge('LOAD')
        return self.uri.replace('{id}', str(token_id))

