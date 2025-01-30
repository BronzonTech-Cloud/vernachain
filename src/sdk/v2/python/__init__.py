"""
Vernachain Python SDK v2

A comprehensive SDK for interacting with the Vernachain blockchain platform.
"""

from .client import VernachainClient
from .types import (
    Transaction,
    Block,
    SmartContract,
    Validator,
    CrossShardTransfer,
    BridgeTransfer
)

__version__ = "2.0.0"
__all__ = [
    'VernachainClient',
    'Transaction',
    'Block',
    'SmartContract',
    'Validator',
    'CrossShardTransfer',
    'BridgeTransfer'
] 