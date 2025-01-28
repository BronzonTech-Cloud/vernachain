from typing import Dict, Any, Optional, Set
from .trie import MerklePatriciaTrie
import time


class StateManager:
    """Manages blockchain state using Merkle Patricia Tries."""
    
    def __init__(self, prune_threshold: int = 1000):
        self.accounts_trie = MerklePatriciaTrie()
        self.storage_tries: Dict[str, MerklePatriciaTrie] = {}
        self.state_roots: Dict[int, str] = {}  # block_number -> state_root
        self.prune_threshold = prune_threshold
        self.last_pruned_block = 0
        
    def update_account(self, address: str, account_data: Dict[str, Any],
                      block_number: int) -> None:
        """
        Update account state.
        
        Args:
            address: Account address
            account_data: Account state data
            block_number: Current block number
        """
        # Update account trie
        self.accounts_trie.put(address, account_data)
        
        # Create storage trie for contract accounts
        if account_data.get('code'):
            if address not in self.storage_tries:
                self.storage_tries[address] = MerklePatriciaTrie()
                
        # Save state root
        self.state_roots[block_number] = self.accounts_trie.root.hash()
        
        # Prune old states if needed
        if block_number - self.last_pruned_block >= self.prune_threshold:
            self._prune_old_states(block_number)
            
    def get_account(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get account state.
        
        Args:
            address: Account address
            
        Returns:
            Dict containing account state if found
        """
        return self.accounts_trie.get(address)
        
    def update_storage(self, address: str, key: str, value: Any,
                      block_number: int) -> None:
        """
        Update contract storage.
        
        Args:
            address: Contract address
            key: Storage key
            value: Storage value
            block_number: Current block number
        """
        if address not in self.storage_tries:
            return
            
        storage_trie = self.storage_tries[address]
        storage_trie.put(key, value)
        
        # Update account storage root
        account = self.get_account(address)
        if account:
            account['storage_root'] = storage_trie.root.hash()
            self.update_account(address, account, block_number)
            
    def get_storage(self, address: str, key: str) -> Optional[Any]:
        """
        Get contract storage value.
        
        Args:
            address: Contract address
            key: Storage key
            
        Returns:
            Storage value if found
        """
        if address not in self.storage_tries:
            return None
            
        return self.storage_tries[address].get(key)
        
    def get_proof(self, address: str, storage_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate Merkle proof for account and storage.
        
        Args:
            address: Account address
            storage_key: Optional storage key
            
        Returns:
            Dict containing account and storage proofs
        """
        proof = {
            'address': address,
            'account_proof': self.accounts_trie.get_proof(address)
        }
        
        if storage_key and address in self.storage_tries:
            proof['storage_proof'] = self.storage_tries[address].get_proof(storage_key)
            
        return proof
        
    def verify_proof(self, proof: Dict[str, Any]) -> bool:
        """
        Verify a state proof.
        
        Args:
            proof: Proof to verify
            
        Returns:
            bool: True if proof is valid
        """
        address = proof['address']
        account = self.get_account(address)
        
        if not account:
            return False
            
        # Verify account proof
        if not self.accounts_trie.verify_proof(
            address,
            account,
            proof['account_proof']
        ):
            return False
            
        # Verify storage proof if present
        if 'storage_proof' in proof and address in self.storage_tries:
            storage_key = proof['storage_key']
            storage_value = self.get_storage(address, storage_key)
            
            if not self.storage_tries[address].verify_proof(
                storage_key,
                storage_value,
                proof['storage_proof']
            ):
                return False
                
        return True
        
    def get_state_root(self, block_number: int) -> Optional[str]:
        """
        Get state root for a block number.
        
        Args:
            block_number: Block number
            
        Returns:
            str: State root hash if found
        """
        return self.state_roots.get(block_number)
        
    def _prune_old_states(self, current_block: int) -> None:
        """
        Prune old state data.
        
        Args:
            current_block: Current block number
        """
        prune_before = current_block - self.prune_threshold
        
        # Remove old state roots
        for block in list(self.state_roots.keys()):
            if block < prune_before:
                del self.state_roots[block]
                
        self.last_pruned_block = current_block
        
    def revert_to_block(self, block_number: int) -> bool:
        """
        Revert state to a previous block.
        
        Args:
            block_number: Block number to revert to
            
        Returns:
            bool: True if revert successful
        """
        state_root = self.state_roots.get(block_number)
        if not state_root:
            return False
            
        # Clear newer state roots
        for block in list(self.state_roots.keys()):
            if block > block_number:
                del self.state_roots[block]
                
        return True 