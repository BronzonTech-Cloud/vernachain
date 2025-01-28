"""
Validator Management System for Vernachain.

This module handles validator reputation, staking rewards, performance tracking,
and advanced validator features including delegation and progressive rewards.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import math
import random

@dataclass
class DelegatorInfo:
    """Information about a delegator."""
    amount: float = 0.0
    since: datetime = field(default_factory=datetime.now)
    rewards: float = 0.0
    last_claim: datetime = field(default_factory=datetime.now)

@dataclass
class ValidatorStats:
    """Statistics for validator performance tracking."""
    blocks_proposed: int = 0
    blocks_signed: int = 0
    missed_blocks: int = 0
    invalid_blocks: int = 0
    double_signs: int = 0
    total_stake: float = 0.0
    self_stake: float = 0.0  # Amount staked by validator themselves
    delegated_stake: float = 0.0  # Amount staked by delegators
    stake_time: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    reputation_score: float = 100.0
    performance_history: List[Tuple[datetime, str, float]] = field(default_factory=list)
    delegators: Dict[str, DelegatorInfo] = field(default_factory=dict)
    commission_rate: float = 0.10  # 10% commission on delegator rewards
    max_commission: float = 0.20  # Maximum commission rate
    unbonding_time: timedelta = field(default_factory=lambda: timedelta(days=14))
    security_deposit: float = 0.0  # Additional security deposit for high-stake validators

class ValidatorManager:
    """Manages validator operations, reputation, and rewards."""
    
    def __init__(self):
        self.validators: Dict[str, ValidatorStats] = {}
        self.active_set: Set[str] = set()
        self.jailed_validators: Set[str] = set()
        self.min_reputation = 50.0
        self.base_reward_rate = 0.05  # 5% annual return
        
        # Enhanced penalty thresholds
        self.penalty_thresholds = {
            'missed_blocks': 10,
            'invalid_blocks': 3,
            'double_signing': 1,
            'low_uptime': 0.95,  # 95% minimum uptime requirement
            'inactivity': timedelta(hours=6)  # Maximum inactivity period
        }
        
        # Enhanced reward multipliers
        self.reward_multipliers = {
            'uptime': 1.2,  # 20% bonus for perfect uptime
            'stake_size': 1.1,  # 10% bonus for large stakes
            'loyalty': 1.15,  # 15% bonus for long-term staking
            'performance': 1.25,  # 25% bonus for consistent good performance
            'security': 1.05  # 5% bonus for additional security deposit
        }
        
        # Progressive staking thresholds
        self.progressive_thresholds = [
            (10000, 1.05),  # 5% bonus for 10k+ stake
            (50000, 1.10),  # 10% bonus for 50k+ stake
            (100000, 1.15),  # 15% bonus for 100k+ stake
            (500000, 1.20)  # 20% bonus for 500k+ stake
        ]
        
        # Security features
        self.max_stake_ratio = 0.10  # Maximum 10% of total stake per validator
        self.min_self_stake_ratio = 0.05  # Minimum 5% self-stake requirement
        self.security_deposit_requirement = 0.02  # 2% security deposit requirement
        
        # Delegation settings
        self.max_delegators = 100  # Maximum delegators per validator
        self.min_delegation = 100.0  # Minimum delegation amount
        self.unbonding_queue: Dict[str, List[Tuple[str, float, datetime]]] = {}
    
    def register_validator(self, address: str, stake_amount: float, security_deposit: float = 0.0) -> bool:
        """Register a new validator with initial stake and security deposit."""
        if address in self.validators:
            return False
            
        # Check minimum self-stake requirement
        total_stake = sum(v.total_stake for v in self.validators.values())
        if total_stake > 0 and stake_amount / (total_stake + stake_amount) > self.max_stake_ratio:
            return False
            
        # Initialize validator
        self.validators[address] = ValidatorStats(
            total_stake=stake_amount,
            self_stake=stake_amount,
            security_deposit=security_deposit
        )
        
        if stake_amount >= self.get_min_stake():
            self.active_set.add(address)
            
        return True
    
    def delegate(self, validator_address: str, delegator_address: str, amount: float) -> bool:
        """Delegate stake to a validator."""
        if validator_address not in self.validators or amount < self.min_delegation:
            return False
            
        stats = self.validators[validator_address]
        
        # Check maximum delegators
        if (len(stats.delegators) >= self.max_delegators and 
            delegator_address not in stats.delegators):
            return False
            
        # Update or add delegator
        if delegator_address in stats.delegators:
            stats.delegators[delegator_address].amount += amount
        else:
            stats.delegators[delegator_address] = DelegatorInfo(amount=amount)
            
        stats.delegated_stake += amount
        stats.total_stake += amount
        return True
    
    def undelegate(self, validator_address: str, delegator_address: str, amount: float) -> bool:
        """Start undelegation process for a delegator."""
        if validator_address not in self.validators:
            return False
            
        stats = self.validators[validator_address]
        if delegator_address not in stats.delegators:
            return False
            
        delegator = stats.delegators[delegator_address]
        if amount > delegator.amount:
            return False
            
        # Add to unbonding queue
        if validator_address not in self.unbonding_queue:
            self.unbonding_queue[validator_address] = []
            
        unbonding_time = datetime.now() + stats.unbonding_time
        self.unbonding_queue[validator_address].append(
            (delegator_address, amount, unbonding_time)
        )
        
        # Update stakes
        delegator.amount -= amount
        stats.delegated_stake -= amount
        stats.total_stake -= amount
        
        # Remove delegator if no stake left
        if delegator.amount == 0:
            del stats.delegators[delegator_address]
            
        return True
    
    def process_unbonding(self) -> List[Tuple[str, str, float]]:
        """Process unbonding requests that have completed their waiting period."""
        now = datetime.now()
        completed = []
        
        for validator_address, queue in self.unbonding_queue.items():
            remaining = []
            for delegator_address, amount, unbonding_time in queue:
                if now >= unbonding_time:
                    completed.append((validator_address, delegator_address, amount))
                else:
                    remaining.append((delegator_address, amount, unbonding_time))
            self.unbonding_queue[validator_address] = remaining
            
        return completed
    
    def update_reputation(self, address: str, block_height: int, event_type: str) -> None:
        """Update validator reputation based on their actions."""
        if address not in self.validators:
            return
            
        stats = self.validators[address]
        
        # Update statistics and performance history
        if event_type == 'block_proposed':
            stats.blocks_proposed += 1
            stats.last_active = datetime.now()
            stats.performance_history.append(
                (datetime.now(), event_type, 1.0)
            )
        elif event_type == 'missed_block':
            stats.missed_blocks += 1
            self._apply_penalty(address, 'missed_blocks', 2.0)
            stats.performance_history.append(
                (datetime.now(), event_type, -2.0)
            )
        elif event_type == 'invalid_block':
            stats.invalid_blocks += 1
            self._apply_penalty(address, 'invalid_blocks', 5.0)
            stats.performance_history.append(
                (datetime.now(), event_type, -5.0)
            )
        elif event_type == 'double_sign':
            stats.double_signs += 1
            self._apply_penalty(address, 'double_signing', 20.0)
            stats.performance_history.append(
                (datetime.now(), event_type, -20.0)
            )
            
        # Check inactivity
        if (datetime.now() - stats.last_active) > self.penalty_thresholds['inactivity']:
            self._apply_penalty(address, 'inactivity', 1.0)
            
        # Maintain performance history
        self._prune_performance_history(stats)
        
        # Check jail conditions
        self._check_jail_conditions(address)
    
    def calculate_rewards(self, address: str, block_height: int) -> Tuple[float, Dict[str, float]]:
        """Calculate rewards for validator and delegators."""
        if address not in self.validators or address in self.jailed_validators:
            return 0.0, {}
            
        stats = self.validators[address]
        base_reward = stats.total_stake * (self.base_reward_rate / (365 * 24 * 60))
        
        # Calculate multipliers
        multiplier = 1.0
        
        # Uptime multiplier
        uptime = self._calculate_uptime(stats)
        if uptime >= 0.99:
            multiplier *= self.reward_multipliers['uptime']
            
        # Progressive stake multiplier
        for threshold, bonus in reversed(self.progressive_thresholds):
            if stats.total_stake >= threshold:
                multiplier *= bonus
                break
                
        # Performance multiplier
        performance_score = self._calculate_performance_score(stats)
        if performance_score >= 0.95:
            multiplier *= self.reward_multipliers['performance']
            
        # Security deposit multiplier
        if stats.security_deposit >= stats.total_stake * self.security_deposit_requirement:
            multiplier *= self.reward_multipliers['security']
            
        # Calculate total reward
        total_reward = base_reward * multiplier * (stats.reputation_score / 100.0)
        
        # Distribute rewards between validator and delegators
        validator_reward = (stats.self_stake / stats.total_stake) * total_reward
        delegator_rewards = {}
        
        for delegator, info in stats.delegators.items():
            delegator_share = (info.amount / stats.total_stake) * total_reward
            commission = delegator_share * stats.commission_rate
            delegator_rewards[delegator] = delegator_share - commission
            validator_reward += commission
            
        return validator_reward, delegator_rewards
    
    def _prune_performance_history(self, stats: ValidatorStats) -> None:
        """Remove old performance history entries."""
        cutoff = datetime.now() - timedelta(days=30)
        stats.performance_history = [
            entry for entry in stats.performance_history
            if entry[0] >= cutoff
        ]
    
    def _calculate_performance_score(self, stats: ValidatorStats) -> float:
        """Calculate performance score based on recent history."""
        if not stats.performance_history:
            return 1.0
            
        total_score = 0.0
        weights = 0.0
        now = datetime.now()
        
        for timestamp, _, score in stats.performance_history:
            age = (now - timestamp).total_seconds() / (30 * 24 * 3600)  # Age in 30-day periods
            weight = math.exp(-age)  # Exponential decay
            total_score += score * weight
            weights += weight
            
        return max(0.0, min(1.0, (total_score / weights + 1.0) / 2.0))
    
    def get_validator_info(self, address: str) -> Optional[Dict]:
        """Get comprehensive information about a validator."""
        stats = self.validators.get(address)
        if not stats:
            return None
            
        return {
            'total_stake': stats.total_stake,
            'self_stake': stats.self_stake,
            'delegated_stake': stats.delegated_stake,
            'reputation_score': stats.reputation_score,
            'commission_rate': stats.commission_rate,
            'uptime': self._calculate_uptime(stats),
            'performance_score': self._calculate_performance_score(stats),
            'is_jailed': address in self.jailed_validators,
            'delegator_count': len(stats.delegators),
            'security_deposit': stats.security_deposit,
            'unbonding_requests': len(self.unbonding_queue.get(address, []))
        }
    
    def update_commission_rate(self, address: str, new_rate: float) -> bool:
        """Update validator's commission rate."""
        if address not in self.validators or new_rate > self.validators[address].max_commission:
            return False
            
        self.validators[address].commission_rate = new_rate
        return True
    
    def add_security_deposit(self, address: str, amount: float) -> bool:
        """Add security deposit for a validator."""
        if address not in self.validators:
            return False
            
        self.validators[address].security_deposit += amount
        return True
    
    def _apply_penalty(self, address: str, violation_type: str, penalty: float) -> None:
        """Apply penalty to validator's reputation score."""
        if address not in self.validators:
            return
            
        stats = self.validators[address]
        stats.reputation_score = max(0.0, stats.reputation_score - penalty)
        
        # Gradually restore reputation if above minimum
        if stats.reputation_score > self.min_reputation:
            restore_amount = min(0.1, 100.0 - stats.reputation_score)
            stats.reputation_score += restore_amount
    
    def _check_jail_conditions(self, address: str) -> None:
        """Check if validator should be jailed based on their behavior."""
        if address not in self.validators:
            return
            
        stats = self.validators[address]
        
        # Check against thresholds
        if (stats.missed_blocks >= self.penalty_thresholds['missed_blocks'] or
            stats.invalid_blocks >= self.penalty_thresholds['invalid_blocks'] or
            stats.double_signs >= self.penalty_thresholds['double_signing']):
            
            self.jail_validator(address)
    
    def jail_validator(self, address: str) -> None:
        """Jail a validator for misbehavior."""
        if address in self.active_set:
            self.active_set.remove(address)
        self.jailed_validators.add(address)
    
    def unjail_validator(self, address: str) -> bool:
        """Attempt to unjail a validator if conditions are met."""
        if address not in self.jailed_validators:
            return False
            
        stats = self.validators[address]
        if stats.reputation_score >= self.min_reputation:
            self.jailed_validators.remove(address)
            if stats.total_stake >= self.get_min_stake():
                self.active_set.add(address)
            return True
        return False
    
    def _calculate_uptime(self, stats: ValidatorStats) -> float:
        """Calculate validator's uptime percentage."""
        total_blocks = stats.blocks_proposed + stats.missed_blocks
        if total_blocks == 0:
            return 1.0
        return stats.blocks_proposed / total_blocks
    
    @staticmethod
    def get_min_stake() -> float:
        """Get minimum stake required for validation."""
        return 1000.0  # Base minimum stake
    
    def get_validator_set(self) -> Set[str]:
        """Get the current set of active validators."""
        return self.active_set.copy()
    
    def get_validator_stats(self, address: str) -> Optional[ValidatorStats]:
        """Get statistics for a specific validator."""
        return self.validators.get(address) 