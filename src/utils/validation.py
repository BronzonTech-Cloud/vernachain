"""Validation utility functions for Vernachain."""

import re
from typing import Any, Dict

def is_valid_address(address: str) -> bool:
    """Validate a blockchain address format.
    
    Args:
        address: Address to validate
        
    Returns:
        bool: True if address is valid
    """
    # Check if address is hex string of correct length (40 chars without 0x prefix)
    if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
        return False
    return True

def is_valid_transaction(transaction: Dict[str, Any]) -> bool:
    """Validate a transaction structure and required fields.
    
    Args:
        transaction: Transaction dict to validate
        
    Returns:
        bool: True if transaction is valid
    """
    required_fields = ['from', 'to', 'value', 'nonce', 'signature']
    
    # Check required fields exist
    if not all(field in transaction for field in required_fields):
        return False
        
    # Validate addresses
    if not is_valid_address(transaction['from']) or not is_valid_address(transaction['to']):
        return False
        
    # Validate value is positive number
    if not isinstance(transaction['value'], (int, float)) or transaction['value'] < 0:
        return False
        
    # Validate nonce is positive integer
    if not isinstance(transaction['nonce'], int) or transaction['nonce'] < 0:
        return False
        
    return True

def is_valid_block(block: Dict[str, Any], previous_block: Dict[str, Any]) -> bool:
    """Validate a block structure and relationship to previous block.
    
    Args:
        block: Block dict to validate
        previous_block: Previous block dict for validation
        
    Returns:
        bool: True if block is valid
    """
    required_fields = ['index', 'timestamp', 'transactions', 'previous_hash', 'validator']
    
    # Check required fields exist
    if not all(field in block for field in required_fields):
        return False
        
    # Validate block index
    if block['index'] != previous_block['index'] + 1:
        return False
        
    # Validate timestamp is after previous block
    if block['timestamp'] <= previous_block['timestamp']:
        return False
        
    # Validate transactions list
    if not isinstance(block['transactions'], list):
        return False
    if not all(is_valid_transaction(tx) for tx in block['transactions']):
        return False
        
    # Validate previous hash matches previous block's hash
    if block['previous_hash'] != previous_block['hash']:
        return False
        
    return True

def is_valid_stake_amount(amount: float) -> bool:
    """Validate a stake amount.
    
    Args:
        amount: Stake amount to validate
        
    Returns:
        bool: True if stake amount is valid
    """
    # Amount must be positive and meet minimum stake requirement
    MIN_STAKE = 1000  # Example minimum stake requirement
    return isinstance(amount, (int, float)) and amount >= MIN_STAKE

def is_valid_contract_code(code: str) -> bool:
    """Validate smart contract code.
    
    Args:
        code: Contract source code to validate
        
    Returns:
        bool: True if contract code is valid
    """
    # Basic validation - check for common security issues
    forbidden_patterns = [
        r'import os',  # No OS operations
        r'import sys',  # No system operations
        r'__import__',  # No dynamic imports
        r'eval\(',     # No eval
        r'exec\(',     # No exec
        r'open\('      # No file operations
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, code):
            return False
            
    return True 