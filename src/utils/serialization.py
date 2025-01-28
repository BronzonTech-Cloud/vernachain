"""Serialization utility functions for Vernachain."""

import json
from typing import Any, Dict
from datetime import datetime

def serialize_transaction(transaction: Dict[str, Any]) -> str:
    """Serialize a transaction to JSON string.
    
    Args:
        transaction: Transaction dict to serialize
        
    Returns:
        str: JSON string representation
    """
    # Convert any datetime objects to ISO format
    tx_copy = transaction.copy()
    if 'timestamp' in tx_copy:
        tx_copy['timestamp'] = tx_copy['timestamp'].isoformat()
        
    # Convert any bytes to hex strings
    if 'signature' in tx_copy and isinstance(tx_copy['signature'], bytes):
        tx_copy['signature'] = tx_copy['signature'].hex()
        
    return json.dumps(tx_copy, sort_keys=True)

def deserialize_transaction(data: str) -> Dict[str, Any]:
    """Deserialize a transaction from JSON string.
    
    Args:
        data: JSON string to deserialize
        
    Returns:
        Dict[str, Any]: Transaction dict
    """
    tx = json.loads(data)
    
    # Convert ISO timestamp back to datetime
    if 'timestamp' in tx:
        tx['timestamp'] = datetime.fromisoformat(tx['timestamp'])
        
    # Convert hex signature back to bytes
    if 'signature' in tx:
        tx['signature'] = bytes.fromhex(tx['signature'])
        
    return tx

def serialize_block(block: Dict[str, Any]) -> str:
    """Serialize a block to JSON string.
    
    Args:
        block: Block dict to serialize
        
    Returns:
        str: JSON string representation
    """
    block_copy = block.copy()
    
    # Convert timestamp to ISO format
    if 'timestamp' in block_copy:
        block_copy['timestamp'] = block_copy['timestamp'].isoformat()
        
    # Serialize transactions
    if 'transactions' in block_copy:
        block_copy['transactions'] = [
            serialize_transaction(tx) if isinstance(tx, dict) else tx
            for tx in block_copy['transactions']
        ]
        
    return json.dumps(block_copy, sort_keys=True)

def deserialize_block(data: str) -> Dict[str, Any]:
    """Deserialize a block from JSON string.
    
    Args:
        data: JSON string to deserialize
        
    Returns:
        Dict[str, Any]: Block dict
    """
    block = json.loads(data)
    
    # Convert ISO timestamp back to datetime
    if 'timestamp' in block:
        block['timestamp'] = datetime.fromisoformat(block['timestamp'])
        
    # Deserialize transactions
    if 'transactions' in block:
        block['transactions'] = [
            deserialize_transaction(tx) if isinstance(tx, str) else tx
            for tx in block['transactions']
        ]
        
    return block

def encode_contract_data(name: str, args: list) -> str:
    """Encode contract function call data.
    
    Args:
        name: Function name
        args: Function arguments
        
    Returns:
        str: Encoded function call data
    """
    return json.dumps({
        'function': name,
        'args': args
    }, sort_keys=True)

def decode_contract_data(data: str) -> tuple:
    """Decode contract function call data.
    
    Args:
        data: Encoded function call data
        
    Returns:
        tuple: (function_name, args)
    """
    decoded = json.loads(data)
    return decoded['function'], decoded['args'] 