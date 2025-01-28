"""Batch operations implementation for the Vernachain SDK."""

import asyncio
from typing import List, Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
from .errors import BatchError, ValidationError

T = TypeVar('T')

@dataclass
class BatchResult(Generic[T]):
    """Result of a batch operation."""
    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None

class BatchProcessor:
    """Processor for batch operations."""
    
    def __init__(self, max_concurrent: int = 10, chunk_size: int = 50):
        """
        Initialize batch processor.
        
        Args:
            max_concurrent: Maximum number of concurrent operations
            chunk_size: Size of chunks for processing
        """
        self.max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_batch(self, items: List[Any], operation: callable) -> List[BatchResult]:
        """
        Process a batch of items.
        
        Args:
            items: List of items to process
            operation: Async function to process each item
            
        Returns:
            List of BatchResult objects
        """
        results: List[BatchResult] = []
        chunks = [items[i:i + self.chunk_size] for i in range(0, len(items), self.chunk_size)]
        
        for chunk in chunks:
            chunk_results = await asyncio.gather(
                *[self._process_item(item, operation) for item in chunk],
                return_exceptions=True
            )
            results.extend(chunk_results)
            
        return results

    async def _process_item(self, item: Any, operation: callable) -> BatchResult:
        """Process a single item with semaphore control."""
        async with self.semaphore:
            try:
                result = await operation(item)
                return BatchResult(success=True, result=result)
            except Exception as e:
                return BatchResult(success=False, error=e)

class BatchBuilder:
    """Builder for constructing batch operations."""
    
    def __init__(self):
        self.operations: List[Dict[str, Any]] = []

    def add_transaction(self, to_address: str, value: float,
                       private_key: str, gas_limit: Optional[int] = None) -> 'BatchBuilder':
        """Add transaction to batch."""
        self.operations.append({
            'type': 'transaction',
            'params': {
                'to_address': to_address,
                'value': value,
                'private_key': private_key,
                'gas_limit': gas_limit
            }
        })
        return self

    def add_contract_deployment(self, bytecode: str, abi: Dict,
                              private_key: str, gas_limit: Optional[int] = None) -> 'BatchBuilder':
        """Add contract deployment to batch."""
        self.operations.append({
            'type': 'deploy_contract',
            'params': {
                'bytecode': bytecode,
                'abi': abi,
                'private_key': private_key,
                'gas_limit': gas_limit
            }
        })
        return self

    def add_contract_call(self, contract_address: str, function_name: str,
                         args: List, abi: Dict) -> 'BatchBuilder':
        """Add contract call to batch."""
        self.operations.append({
            'type': 'contract_call',
            'params': {
                'contract_address': contract_address,
                'function_name': function_name,
                'args': args,
                'abi': abi
            }
        })
        return self

    def add_bridge_transfer(self, from_chain: str, to_chain: str,
                          token: str, amount: float, to_address: str,
                          private_key: str) -> 'BatchBuilder':
        """Add bridge transfer to batch."""
        self.operations.append({
            'type': 'bridge_transfer',
            'params': {
                'from_chain': from_chain,
                'to_chain': to_chain,
                'token': token,
                'amount': amount,
                'to_address': to_address,
                'private_key': private_key
            }
        })
        return self

    def build(self) -> List[Dict[str, Any]]:
        """Build the batch operations list."""
        if not self.operations:
            raise BatchError("No operations added to batch")
        return self.operations 