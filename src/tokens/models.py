"""Token models for managing token data."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set
import secrets
from decimal import Decimal


@dataclass
class TokenMetadata:
    """Token metadata."""
    name: str
    symbol: str
    description: str
    image_url: Optional[str] = None
    website: Optional[str] = None
    socials: Dict[str, str] = field(default_factory=dict)  # platform -> url
    tags: List[str] = field(default_factory=list)


@dataclass
class TokenPermissions:
    """Token permissions."""
    can_mint: bool = False
    can_burn: bool = False
    can_transfer: bool = False
    is_admin: bool = False


@dataclass
class TokenAnalytics:
    """Token analytics data."""
    price_usd: float = 0.0
    market_cap: float = 0.0
    volume_24h: float = 0.0
    price_change_24h: float = 0.0
    holders_count: int = 0
    transactions_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TokenTransaction:
    """Token transaction data."""
    tx_hash: str
    from_address: str
    to_address: str
    amount: Decimal
    timestamp: datetime
    type: str  # transfer, mint, burn, stake, unstake
    status: str = "pending"  # pending, confirmed, failed


@dataclass
class VestingSchedule:
    """Token vesting schedule."""
    beneficiary: str
    total_amount: Decimal
    start_time: datetime
    cliff_duration: int  # seconds
    vesting_duration: int  # seconds
    released_amount: Decimal = Decimal(0)
    revoked: bool = False


@dataclass
class GovernanceProposal:
    """Token governance proposal."""
    id: int
    creator: str
    description: str
    actions: List[Dict]
    for_votes: Decimal = Decimal(0)
    against_votes: Decimal = Decimal(0)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    executed: bool = False
    status: str = "pending"  # pending, active, succeeded, defeated, executed, cancelled


@dataclass
class Token:
    """Token data model."""
    metadata: TokenMetadata
    owner_address: str
    decimals: int = 18
    is_mintable: bool = True
    is_burnable: bool = False
    is_pausable: bool = True
    
    # Contract addresses
    contract_address: Optional[str] = None
    governance_address: Optional[str] = None
    vesting_address: Optional[str] = None
    
    # Token state
    total_supply: Decimal = Decimal(0)
    circulating_supply: Decimal = Decimal(0)
    is_frozen: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_minted: Optional[datetime] = None
    
    # Balances and allowances
    balances: Dict[str, Decimal] = field(default_factory=dict)  # address -> balance
    allowances: Dict[str, Dict[str, Decimal]] = field(default_factory=dict)  # owner -> spender -> amount
    
    # Governance
    proposals: List[GovernanceProposal] = field(default_factory=list)
    proposal_count: int = 0
    quorum: Decimal = Decimal("0.04")  # 4% of total supply
    voting_delay: int = 1  # blocks
    voting_period: int = 3 * 24 * 3600  # seconds (3 days)
    
    # Vesting
    vesting_schedules: List[VestingSchedule] = field(default_factory=list)
    
    # Analytics and history
    holders: Dict[str, Decimal] = field(default_factory=dict)  # address -> balance
    minting_history: List[Dict] = field(default_factory=list)
    permissions: Dict[str, TokenPermissions] = field(default_factory=dict)  # address -> permissions
    transactions: List[TokenTransaction] = field(default_factory=list)
    analytics: TokenAnalytics = field(default_factory=TokenAnalytics)
    
    def grant_permission(self, address: str, permission_type: str) -> bool:
        """
        Grant permission to an address.
        
        Args:
            address: Address to grant permission to
            permission_type: Type of permission (mint, burn, transfer, admin)
            
        Returns:
            bool: True if permission granted
        """
        if address not in self.permissions:
            self.permissions[address] = TokenPermissions()
            
        perms = self.permissions[address]
        if permission_type == 'mint':
            perms.can_mint = True
        elif permission_type == 'burn':
            perms.can_burn = True
        elif permission_type == 'transfer':
            perms.can_transfer = True
        elif permission_type == 'admin':
            perms.is_admin = True
        else:
            return False
            
        self.updated_at = datetime.utcnow()
        return True
    
    def revoke_permission(self, address: str, permission_type: str) -> bool:
        """Revoke permission from an address."""
        if address not in self.permissions:
            return False
            
        perms = self.permissions[address]
        if permission_type == 'mint':
            perms.can_mint = False
        elif permission_type == 'burn':
            perms.can_burn = False
        elif permission_type == 'transfer':
            perms.can_transfer = False
        elif permission_type == 'admin':
            perms.is_admin = False
        else:
            return False
            
        self.updated_at = datetime.utcnow()
        return True
    
    def check_permission(self, address: str, permission_type: str) -> bool:
        """Check if address has specific permission."""
        if address == self.owner_address:  # Owner has all permissions
            return True
            
        if address not in self.permissions:
            return False
            
        perms = self.permissions[address]
        if permission_type == 'mint':
            return perms.can_mint
        elif permission_type == 'burn':
            return perms.can_burn
        elif permission_type == 'transfer':
            return perms.can_transfer
        elif permission_type == 'admin':
            return perms.is_admin
            
        return False
    
    def record_transaction(self, tx_type: str, from_address: Optional[str],
                         to_address: Optional[str], amount: Decimal,
                         tx_hash: Optional[str] = None) -> None:
        """Record a token transaction."""
        tx = TokenTransaction(
            tx_hash=tx_hash or f"tx_{len(self.transactions)}",
            from_address=from_address or self.owner_address,
            to_address=to_address or self.owner_address,
            amount=amount,
            timestamp=datetime.utcnow(),
            type=tx_type,
            status="confirmed"
        )
        
        self.transactions.append(tx)
        self.update_analytics(tx)
    
    def update_analytics(self, tx: TokenTransaction) -> None:
        """Update analytics based on transaction."""
        # Update transaction counts
        if tx.type == 'transfer':
            self.analytics.transactions_count += 1
        
        # Update daily volume
        date_str = tx.timestamp.date().isoformat()
        self.analytics.volume_24h += float(tx.amount)
        
        # Update unique holders
        self.analytics.holders_count = len(self.holders)
        
        # Update holder distribution
        self.update_holder_distribution()
    
    def update_holder_distribution(self) -> None:
        """Update holder distribution analytics."""
        distribution = {
            '0-100': 0,
            '100-1K': 0,
            '1K-10K': 0,
            '10K-100K': 0,
            '100K+': 0
        }
        
        for balance in self.holders.values():
            if balance == 0:
                continue
            elif balance <= 100:
                distribution['0-100'] += 1
            elif balance <= 1000:
                distribution['100-1K'] += 1
            elif balance <= 10000:
                distribution['1K-10K'] += 1
            elif balance <= 100000:
                distribution['10K-100K'] += 1
            else:
                distribution['100K+'] += 1
        
        self.analytics.holder_distribution = distribution
    
    def get_analytics(self) -> Dict:
        """Get comprehensive analytics data."""
        return {
            'total_transfers': self.analytics.transactions_count,
            'total_mints': len(self.minting_history),
            'total_burns': len([
                tx for tx in self.transactions
                if tx.type == 'burn'
            ]),
            'unique_holders': self.analytics.holders_count,
            'daily_volume': self.analytics.volume_24h,
            'holder_distribution': self.analytics.holder_distribution,
            'price_history': {
                tx.timestamp.isoformat(): float(tx.amount)
                for tx in self.transactions
                if tx.type == 'transfer'
            },
            'supply_metrics': {
                'total_supply': str(self.total_supply),
                'circulating_supply': str(self.circulating_supply),
                'burned': str(self.total_supply - self.circulating_supply)
            },
            'transaction_metrics': {
                'last_24h': len([
                    tx for tx in self.transactions
                    if datetime.utcnow() - tx.timestamp <= timedelta(days=1)
                ]),
                'last_7d': len([
                    tx for tx in self.transactions
                    if datetime.utcnow() - tx.timestamp <= timedelta(days=7)
                ])
            }
        }
    
    def mint(self, amount: Decimal, to_address: str) -> bool:
        """Mint new tokens."""
        if not self.is_mintable or self.is_frozen:
            return False
            
        self.total_supply += amount
        self.circulating_supply += amount
        self.balances[to_address] = self.balances.get(to_address, Decimal(0)) + amount
        self.holders[to_address] = self.balances[to_address]
        
        self.minting_history.append({
            'amount': amount,
            'to_address': to_address,
            'timestamp': datetime.utcnow()
        })
        
        self.last_minted = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True
    
    def burn(self, amount: Decimal, from_address: str) -> bool:
        """Burn tokens."""
        if not self.is_burnable or self.is_frozen:
            return False
            
        if self.balances.get(from_address, Decimal(0)) < amount:
            return False
            
        self.total_supply -= amount
        self.circulating_supply -= amount
        self.balances[from_address] -= amount
        self.holders[from_address] = self.balances[from_address]
        
        if self.balances[from_address] == 0:
            del self.balances[from_address]
            del self.holders[from_address]
            
        self.updated_at = datetime.utcnow()
        return True
    
    def transfer(self, from_address: str, to_address: str, amount: Decimal) -> bool:
        """Transfer tokens."""
        if self.is_frozen or self.balances.get(from_address, Decimal(0)) < amount:
            return False
            
        self.balances[from_address] -= amount
        self.balances[to_address] = self.balances.get(to_address, Decimal(0)) + amount
        
        self.holders[from_address] = self.balances[from_address]
        self.holders[to_address] = self.balances[to_address]
        
        if self.balances[from_address] == 0:
            del self.balances[from_address]
            del self.holders[from_address]
            
        tx = TokenTransaction(
            tx_hash=f"tx_{len(self.transactions)}",
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            timestamp=datetime.utcnow(),
            type="transfer",
            status="confirmed"
        )
        self.transactions.append(tx)
        
        self.analytics.transactions_count += 1
        self.analytics.holders_count = len(self.holders)
        self.updated_at = datetime.utcnow()
        return True
    
    def approve(self, owner: str, spender: str, amount: Decimal) -> bool:
        """Approve token spending."""
        if self.is_frozen:
            return False
            
        if owner not in self.allowances:
            self.allowances[owner] = {}
            
        self.allowances[owner][spender] = amount
        self.updated_at = datetime.utcnow()
        return True
    
    def transfer_from(self, spender: str, from_address: str, to_address: str, amount: Decimal) -> bool:
        """Transfer tokens on behalf of owner."""
        if self.is_frozen:
            return False
            
        allowed = self.allowances.get(from_address, {}).get(spender, Decimal(0))
        if allowed < amount or self.balances.get(from_address, Decimal(0)) < amount:
            return False
            
        self.allowances[from_address][spender] -= amount
        return self.transfer(from_address, to_address, amount)
    
    def create_proposal(self, creator: str, description: str, actions: List[Dict]) -> Optional[int]:
        """Create governance proposal."""
        if not self.governance_address or self.balances.get(creator, Decimal(0)) < (self.total_supply * Decimal("0.01")):
            return None
            
        self.proposal_count += 1
        proposal = GovernanceProposal(
            id=self.proposal_count,
            creator=creator,
            description=description,
            actions=actions,
            start_time=datetime.utcnow() + datetime.timedelta(blocks=self.voting_delay),
            end_time=datetime.utcnow() + datetime.timedelta(seconds=self.voting_period)
        )
        
        self.proposals.append(proposal)
        self.updated_at = datetime.utcnow()
        return proposal.id
    
    def vote_on_proposal(self, proposal_id: int, voter: str, support: bool) -> bool:
        """Vote on governance proposal."""
        if not self.governance_address:
            return False
            
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal or proposal.status != "active":
            return False
            
        vote_weight = self.balances.get(voter, Decimal(0))
        if support:
            proposal.for_votes += vote_weight
        else:
            proposal.against_votes += vote_weight
            
        self.updated_at = datetime.utcnow()
        return True
    
    def create_vesting_schedule(
        self,
        beneficiary: str,
        total_amount: Decimal,
        cliff_duration: int,
        vesting_duration: int
    ) -> bool:
        """Create token vesting schedule."""
        if not self.vesting_address or self.balances.get(self.owner_address, Decimal(0)) < total_amount:
            return False
            
        schedule = VestingSchedule(
            beneficiary=beneficiary,
            total_amount=total_amount,
            start_time=datetime.utcnow(),
            cliff_duration=cliff_duration,
            vesting_duration=vesting_duration
        )
        
        self.vesting_schedules.append(schedule)
        return self.transfer(self.owner_address, self.vesting_address, total_amount)
    
    def release_vested_tokens(self, beneficiary: str) -> Decimal:
        """Release vested tokens for beneficiary."""
        if not self.vesting_address:
            return Decimal(0)
            
        schedule = next((s for s in self.vesting_schedules if s.beneficiary == beneficiary), None)
        if not schedule or schedule.revoked:
            return Decimal(0)
            
        vested_amount = self._calculate_vested_amount(schedule)
        releasable = vested_amount - schedule.released_amount
        
        if releasable > 0 and self.transfer(self.vesting_address, beneficiary, releasable):
            schedule.released_amount += releasable
            return releasable
            
        return Decimal(0)
    
    def _calculate_vested_amount(self, schedule: VestingSchedule) -> Decimal:
        """Calculate vested amount for schedule."""
        if schedule.revoked:
            return Decimal(0)
            
        now = datetime.utcnow()
        time_from_start = (now - schedule.start_time).total_seconds()
        
        if time_from_start < schedule.cliff_duration:
            return Decimal(0)
            
        if time_from_start >= schedule.vesting_duration:
            return schedule.total_amount
            
        return schedule.total_amount * Decimal(time_from_start) / Decimal(schedule.vesting_duration)
    
    def freeze(self) -> None:
        """Freeze all token transfers."""
        self.is_frozen = True
        self.updated_at = datetime.utcnow()
    
    def unfreeze(self) -> None:
        """Unfreeze token transfers."""
        self.is_frozen = False
        self.updated_at = datetime.utcnow()
    
    def disable_minting(self) -> None:
        """Disable future minting."""
        self.is_mintable = False
        self.updated_at = datetime.utcnow() 