import random
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class Validator:
    """Represents a validator in the PoS system."""
    address: str
    stake: float
    is_active: bool = True
    last_block_time: float = field(default_factory=time.time)
    consecutive_misses: int = 0
    slashed_amount: float = 0.0

    def slash(self, amount: float) -> float:
        """
        Slash the validator's stake.
        
        Args:
            amount: Amount to slash
            
        Returns:
            float: Actually slashed amount
        """
        slash_amount = min(amount, self.stake)
        self.stake -= slash_amount
        self.slashed_amount += slash_amount
        return slash_amount


@dataclass
class ProofOfStake:
    """Implements the Proof of Stake consensus mechanism."""
    # Minimum stake required to become a validator
    MIN_STAKE: float = 100.0
    # Maximum stake that counts towards validation probability
    MAX_EFFECTIVE_STAKE: float = 10000.0
    # Time window for block production (seconds)
    BLOCK_TIME_WINDOW: float = 60.0
    # Number of consecutive missed blocks before penalty
    MAX_MISSED_BLOCKS: int = 3
    # Percentage of stake to slash for misbehavior
    SLASH_PERCENTAGE: float = 0.1
    
    validators: Dict[str, Validator] = field(default_factory=dict)
    active_set: Set[str] = field(default_factory=set)
    
    def add_validator(self, address: str, stake: float) -> bool:
        """
        Add a new validator to the set.
        
        Args:
            address: Validator's address
            stake: Amount to stake
            
        Returns:
            bool: True if validator was added successfully
        """
        if stake < self.MIN_STAKE:
            return False
            
        effective_stake = min(stake, self.MAX_EFFECTIVE_STAKE)
        
        if address in self.validators:
            # Update existing validator's stake
            validator = self.validators[address]
            validator.stake = effective_stake
            validator.is_active = True
            self.active_set.add(address)
        else:
            # Create new validator
            self.validators[address] = Validator(
                address=address,
                stake=effective_stake
            )
            self.active_set.add(address)
            
        return True

    def remove_validator(self, address: str) -> bool:
        """
        Remove a validator from the set.
        
        Args:
            address: Validator's address
            
        Returns:
            bool: True if validator was removed
        """
        if address in self.validators:
            self.active_set.discard(address)
            del self.validators[address]
            return True
        return False

    def select_validator(self) -> Optional[Validator]:
        """
        Select a validator for the next block based on stake weight.
        
        Returns:
            Validator if one is selected, None otherwise
        """
        if not self.active_set:
            return None
            
        # Calculate total active stake
        total_stake = sum(
            self.validators[addr].stake 
            for addr in self.active_set
        )
        
        if total_stake == 0:
            return None
            
        # Select validator based on weighted probability
        selection_point = random.uniform(0, total_stake)
        current_sum = 0
        
        for address in self.active_set:
            validator = self.validators[address]
            current_sum += validator.stake
            if current_sum >= selection_point:
                return validator
                
        # Fallback to first active validator (shouldn't normally happen)
        return self.validators[next(iter(self.active_set))]

    def validate_block_time(self, validator: Validator, block_time: float) -> bool:
        """
        Validate that the block is being produced in the correct time window.
        
        Args:
            validator: Validator producing the block
            block_time: Time the block is being produced
            
        Returns:
            bool: True if the block time is valid
        """
        time_since_last = block_time - validator.last_block_time
        return time_since_last >= self.BLOCK_TIME_WINDOW

    def record_block_production(self, validator_address: str, success: bool) -> None:
        """
        Record the result of a block production attempt.
        
        Args:
            validator_address: Address of the validator
            success: Whether the block was successfully produced
        """
        if validator_address not in self.validators:
            return
            
        validator = self.validators[validator_address]
        
        if success:
            validator.consecutive_misses = 0
            validator.last_block_time = time.time()
        else:
            validator.consecutive_misses += 1
            
            # Apply penalties for consecutive misses
            if validator.consecutive_misses >= self.MAX_MISSED_BLOCKS:
                self.slash_validator(
                    validator_address,
                    validator.stake * self.SLASH_PERCENTAGE
                )

    def slash_validator(self, address: str, amount: float) -> float:
        """
        Slash a validator's stake for misbehavior.
        
        Args:
            address: Validator's address
            amount: Amount to slash
            
        Returns:
            float: Actually slashed amount
        """
        if address not in self.validators:
            return 0.0
            
        validator = self.validators[address]
        slashed = validator.slash(amount)
        
        # Remove validator if stake falls below minimum
        if validator.stake < self.MIN_STAKE:
            self.active_set.discard(address)
            validator.is_active = False
            
        return slashed

    def get_validator_info(self, address: str) -> Optional[Dict]:
        """
        Get information about a validator.
        
        Args:
            address: Validator's address
            
        Returns:
            Dict containing validator information if found
        """
        if address not in self.validators:
            return None
            
        validator = self.validators[address]
        return {
            "address": validator.address,
            "stake": validator.stake,
            "is_active": validator.is_active,
            "last_block_time": validator.last_block_time,
            "consecutive_misses": validator.consecutive_misses,
            "slashed_amount": validator.slashed_amount
        }

    def get_active_validators(self) -> List[Dict]:
        """
        Get list of active validators.
        
        Returns:
            List of validator information dictionaries
        """
        return [
            self.get_validator_info(addr)
            for addr in self.active_set
        ]

    def calculate_rewards(self, block_reward: float) -> Dict[str, float]:
        """
        Calculate rewards for all active validators based on their stake.
        
        Args:
            block_reward: Total reward for the block
            
        Returns:
            Dict mapping validator addresses to their rewards
        """
        if not self.active_set:
            return {}
            
        total_stake = sum(
            self.validators[addr].stake 
            for addr in self.active_set
        )
        
        if total_stake == 0:
            return {}
            
        rewards = {}
        for address in self.active_set:
            validator = self.validators[address]
            reward = (validator.stake / total_stake) * block_reward
            rewards[address] = reward
            
        return rewards 