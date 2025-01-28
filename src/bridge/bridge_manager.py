"""
Cross-Chain Bridge Manager for Vernachain.

This module handles cross-chain transactions, asset locking/unlocking,
and bridge validator management for secure cross-chain operations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import hashlib
import json

class ChainType(Enum):
    """Supported blockchain types."""
    ETHEREUM = "ethereum"
    BINANCE = "binance"
    POLYGON = "polygon"
    VERNACHAIN = "vernachain"

class BridgeStatus(Enum):
    """Status of bridge transactions."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERTED = "reverted"

@dataclass
class ChainConfig:
    """Configuration for connected chains."""
    chain_type: ChainType
    chain_id: int
    rpc_endpoint: str
    required_confirmations: int
    gas_limit: int
    bridge_contract_address: str
    token_contracts: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    last_synced_block: int = 0

@dataclass
class BridgeTransaction:
    """Cross-chain bridge transaction details."""
    tx_hash: str
    from_chain: ChainType
    to_chain: ChainType
    from_address: str
    to_address: str
    token_symbol: str
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: BridgeStatus = BridgeStatus.PENDING
    confirmations: int = 0
    source_tx_hash: Optional[str] = None
    target_tx_hash: Optional[str] = None
    merkle_proof: List[str] = field(default_factory=list)
    signatures: List[Tuple[str, bytes]] = field(default_factory=list)

class BridgeManager:
    """Manages cross-chain bridge operations and security."""
    
    def __init__(self, min_validators: int = 3):
        self.chains: Dict[ChainType, ChainConfig] = {}
        self.bridge_validators: Set[str] = set()
        self.min_validators = min_validators
        self.transactions: Dict[str, BridgeTransaction] = {}
        self.locked_assets: Dict[str, float] = {}  # token -> amount
        self.nonces: Dict[str, int] = {}  # address -> nonce
        
        # Security settings
        self.max_transfer_limit = 1000000.0  # Maximum transfer amount
        self.daily_volume_limit = 5000000.0  # Maximum daily volume
        self.daily_volumes: Dict[str, float] = {}  # token -> daily volume
        self.last_volume_reset = datetime.now()
        
        # Bridge fees
        self.base_fee = 0.001  # 0.1% base fee
        self.fee_multipliers = {
            ChainType.ETHEREUM: 1.5,  # 50% higher for Ethereum due to gas costs
            ChainType.BINANCE: 1.0,
            ChainType.POLYGON: 1.2,
            ChainType.VERNACHAIN: 0.5  # 50% discount for internal chain
        }
    
    def register_chain(self, config: ChainConfig) -> bool:
        """Register a new chain for bridging."""
        if config.chain_type in self.chains:
            return False
            
        self.chains[config.chain_type] = config
        return True
    
    def add_bridge_validator(self, validator_address: str) -> bool:
        """Add a validator for bridge operations."""
        if validator_address in self.bridge_validators:
            return False
            
        self.bridge_validators.add(validator_address)
        return True
    
    def initiate_transfer(self, from_chain: ChainType, to_chain: ChainType,
                         from_address: str, to_address: str, token: str,
                         amount: float) -> Optional[str]:
        """
        Initiate a cross-chain transfer.
        
        Args:
            from_chain: Source chain type
            to_chain: Target chain type
            from_address: Source address
            to_address: Target address
            token: Token symbol
            amount: Amount to transfer
            
        Returns:
            str: Transaction hash if successful
        """
        # Validate chains
        if not (from_chain in self.chains and to_chain in self.chains):
            return None
            
        # Check if chains are active
        if not (self.chains[from_chain].is_active and self.chains[to_chain].is_active):
            return None
            
        # Validate transfer limits
        if amount > self.max_transfer_limit:
            return None
            
        # Check daily volume limits
        if not self._check_and_update_volume(token, amount):
            return None
            
        # Calculate fee
        fee = self._calculate_fee(from_chain, to_chain, amount)
        
        # Generate transaction hash
        nonce = self._get_next_nonce(from_address)
        tx_data = {
            'from_chain': from_chain.value,
            'to_chain': to_chain.value,
            'from_address': from_address,
            'to_address': to_address,
            'token': token,
            'amount': amount,
            'fee': fee,
            'nonce': nonce,
            'timestamp': datetime.now().isoformat()
        }
        tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
        
        # Create bridge transaction
        self.transactions[tx_hash] = BridgeTransaction(
            tx_hash=tx_hash,
            from_chain=from_chain,
            to_chain=to_chain,
            from_address=from_address,
            to_address=to_address,
            token_symbol=token,
            amount=amount
        )
        
        # Lock assets
        self._lock_assets(token, amount + fee)
        
        return tx_hash
    
    def validate_transfer(self, tx_hash: str, validator_address: str,
                         signature: bytes) -> bool:
        """
        Validate a cross-chain transfer.
        
        Args:
            tx_hash: Transaction hash
            validator_address: Validator's address
            signature: Validator's signature
            
        Returns:
            bool: True if validation successful
        """
        if tx_hash not in self.transactions:
            return False
            
        if validator_address not in self.bridge_validators:
            return False
            
        tx = self.transactions[tx_hash]
        
        # Check if validator hasn't already signed
        if any(addr == validator_address for addr, _ in tx.signatures):
            return False
            
        # Add signature
        tx.signatures.append((validator_address, signature))
        
        # Check if we have enough signatures
        if len(tx.signatures) >= self.min_validators:
            tx.status = BridgeStatus.PROCESSING
            
        return True
    
    def complete_transfer(self, tx_hash: str, target_tx_hash: str) -> bool:
        """
        Complete a cross-chain transfer.
        
        Args:
            tx_hash: Original transaction hash
            target_tx_hash: Transaction hash on target chain
            
        Returns:
            bool: True if completion successful
        """
        if tx_hash not in self.transactions:
            return False
            
        tx = self.transactions[tx_hash]
        
        if tx.status != BridgeStatus.PROCESSING:
            return False
            
        # Update transaction status
        tx.status = BridgeStatus.COMPLETED
        tx.target_tx_hash = target_tx_hash
        
        # Unlock assets on target chain
        self._unlock_assets(tx.token_symbol, tx.amount)
        
        return True
    
    def revert_transfer(self, tx_hash: str, reason: str) -> bool:
        """
        Revert a failed transfer.
        
        Args:
            tx_hash: Transaction hash
            reason: Reason for reversion
            
        Returns:
            bool: True if reversion successful
        """
        if tx_hash not in self.transactions:
            return False
            
        tx = self.transactions[tx_hash]
        
        if tx.status == BridgeStatus.COMPLETED:
            return False
            
        # Update transaction status
        tx.status = BridgeStatus.REVERTED
        
        # Unlock assets on source chain
        self._unlock_assets(tx.token_symbol, tx.amount)
        
        return True
    
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict]:
        """Get detailed status of a bridge transaction."""
        tx = self.transactions.get(tx_hash)
        if not tx:
            return None
            
        return {
            'status': tx.status.value,
            'from_chain': tx.from_chain.value,
            'to_chain': tx.to_chain.value,
            'amount': tx.amount,
            'token': tx.token_symbol,
            'confirmations': tx.confirmations,
            'signatures': len(tx.signatures),
            'timestamp': tx.timestamp.isoformat(),
            'source_tx': tx.source_tx_hash,
            'target_tx': tx.target_tx_hash
        }
    
    def _calculate_fee(self, from_chain: ChainType, to_chain: ChainType,
                      amount: float) -> float:
        """Calculate bridge fee based on chains and amount."""
        base = amount * self.base_fee
        multiplier = max(self.fee_multipliers[from_chain],
                        self.fee_multipliers[to_chain])
        return base * multiplier
    
    def _check_and_update_volume(self, token: str, amount: float) -> bool:
        """Check and update daily volume limits."""
        now = datetime.now()
        
        # Reset daily volumes if needed
        if (now - self.last_volume_reset).days >= 1:
            self.daily_volumes = {}
            self.last_volume_reset = now
            
        current_volume = self.daily_volumes.get(token, 0.0)
        if current_volume + amount > self.daily_volume_limit:
            return False
            
        self.daily_volumes[token] = current_volume + amount
        return True
    
    def _get_next_nonce(self, address: str) -> int:
        """Get next nonce for an address."""
        nonce = self.nonces.get(address, 0)
        self.nonces[address] = nonce + 1
        return nonce
    
    def _lock_assets(self, token: str, amount: float) -> None:
        """Lock assets in the bridge contract."""
        current = self.locked_assets.get(token, 0.0)
        self.locked_assets[token] = current + amount
    
    def _unlock_assets(self, token: str, amount: float) -> None:
        """Unlock assets from the bridge contract."""
        current = self.locked_assets.get(token, 0.0)
        self.locked_assets[token] = max(0.0, current - amount)
    
    def get_bridge_stats(self) -> Dict:
        """Get bridge statistics and status."""
        return {
            'active_chains': [
                {
                    'type': chain_type.value,
                    'id': config.chain_id,
                    'is_active': config.is_active,
                    'last_synced': config.last_synced_block
                }
                for chain_type, config in self.chains.items()
            ],
            'validator_count': len(self.bridge_validators),
            'locked_assets': self.locked_assets.copy(),
            'daily_volumes': self.daily_volumes.copy(),
            'pending_transactions': len([
                tx for tx in self.transactions.values()
                if tx.status == BridgeStatus.PENDING
            ]),
            'processing_transactions': len([
                tx for tx in self.transactions.values()
                if tx.status == BridgeStatus.PROCESSING
            ])
        } 