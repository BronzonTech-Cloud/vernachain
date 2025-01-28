from typing import List, Dict, Any, Optional
from .transaction import Transaction


class TransactionPool:
    def __init__(self):
        """Initialize an empty transaction pool."""
        self.pending_transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to the pool if it's valid.
        
        Args:
            transaction: Transaction to add to the pool
            
        Returns:
            bool: True if transaction was added successfully, False otherwise
        """
        if not transaction.is_valid():
            return False
            
        # Check if transaction already exists in pool
        if any(t.transaction_id == transaction.transaction_id for t in self.pending_transactions):
            return False
            
        self.pending_transactions.append(transaction)
        return True

    def remove_transaction(self, transaction_id: str) -> bool:
        """
        Remove a transaction from the pool by its ID.
        
        Args:
            transaction_id: ID of the transaction to remove
            
        Returns:
            bool: True if transaction was removed, False if not found
        """
        initial_length = len(self.pending_transactions)
        self.pending_transactions = [t for t in self.pending_transactions 
                                   if t.transaction_id != transaction_id]
        return len(self.pending_transactions) < initial_length

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction from the pool by its ID.
        
        Args:
            transaction_id: ID of the transaction to retrieve
            
        Returns:
            Transaction if found, None otherwise
        """
        for transaction in self.pending_transactions:
            if transaction.transaction_id == transaction_id:
                return transaction
        return None

    def get_transactions(self, limit: int = None) -> List[Transaction]:
        """
        Get a list of pending transactions.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of pending transactions
        """
        if limit is None:
            return self.pending_transactions.copy()
        return self.pending_transactions[:limit]

    def clear(self) -> None:
        """Clear all pending transactions from the pool."""
        self.pending_transactions.clear()

    def remove_transactions(self, transactions: List[Transaction]) -> None:
        """
        Remove multiple transactions from the pool.
        
        Args:
            transactions: List of transactions to remove
        """
        transaction_ids = {t.transaction_id for t in transactions}
        self.pending_transactions = [t for t in self.pending_transactions 
                                   if t.transaction_id not in transaction_ids]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction pool to a dictionary representation.
        
        Returns:
            Dict containing the pool's data
        """
        return {
            "pending_transactions": [t.to_dict() for t in self.pending_transactions]
        }

    @staticmethod
    def from_dict(pool_dict: Dict[str, Any]) -> 'TransactionPool':
        """
        Create a TransactionPool instance from a dictionary representation.
        
        Args:
            pool_dict: Dictionary containing pool data
            
        Returns:
            TransactionPool: A new TransactionPool instance
        """
        pool = TransactionPool()
        pool.pending_transactions = [
            Transaction.from_dict(t) for t in pool_dict["pending_transactions"]
        ]
        return pool 