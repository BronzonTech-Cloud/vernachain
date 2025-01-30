"""Token vesting contract for managing token vesting schedules."""

from typing import Dict, List
from datetime import datetime

class VestingSchedule:
    def __init__(self, beneficiary: str, total_amount: float, start_time: int,
                 cliff_duration: int, vesting_duration: int):
        self.beneficiary = beneficiary
        self.total_amount = total_amount
        self.start_time = start_time
        self.cliff_duration = cliff_duration
        self.vesting_duration = vesting_duration
        self.released_amount = 0.0
        self.revoked = False

class TokenVesting:
    """Contract for managing token vesting schedules."""
    
    def __init__(self, token_address: str):
        """
        Initialize vesting contract.
        
        Args:
            token_address: Address of token to vest
        """
        self.token_address = token_address
        self.schedules = []  # List of VestingSchedule
        self.owner = globals()['sender']
        
    def create_vesting_schedule(
        self,
        beneficiary: str,
        total_amount: float,
        cliff_duration: int,  # Duration in seconds
        vesting_duration: int  # Duration in seconds
    ) -> bool:
        """
        Create a new vesting schedule.
        
        Args:
            beneficiary: Address of beneficiary
            total_amount: Total amount of tokens to vest
            cliff_duration: Duration of cliff period in seconds
            vesting_duration: Total vesting duration in seconds
            
        Returns:
            bool: True if schedule creation successful
        """
        if globals()['sender'] != self.owner:
            return False
            
        # Check if beneficiary already has a schedule
        for schedule in self.schedules:
            if schedule.beneficiary == beneficiary:
                return False
                
        # Transfer tokens to contract
        token = globals()['contracts'][self.token_address]
        if not token.transfer_from(globals()['sender'], globals()['contract_address'], total_amount):
            return False
            
        schedule = VestingSchedule(
            beneficiary=beneficiary,
            total_amount=total_amount,
            start_time=globals()['block_timestamp'],
            cliff_duration=cliff_duration,
            vesting_duration=vesting_duration
        )
        
        self.schedules.append(schedule)
        return True
        
    def release(self) -> float:
        """
        Release vested tokens for sender.
        
        Returns:
            float: Amount of tokens released
        """
        schedule = self._get_schedule(globals()['sender'])
        if not schedule:
            return 0
            
        releasable = self._get_releasable_amount(schedule)
        if releasable == 0:
            return 0
            
        schedule.released_amount += releasable
        
        # Transfer tokens to beneficiary
        token = globals()['contracts'][self.token_address]
        if not token.transfer(schedule.beneficiary, releasable):
            return 0
            
        return releasable
        
    def revoke(self, beneficiary: str) -> bool:
        """
        Revoke vesting schedule (only owner).
        
        Args:
            beneficiary: Address of beneficiary
            
        Returns:
            bool: True if revocation successful
        """
        if globals()['sender'] != self.owner:
            return False
            
        schedule = self._get_schedule(beneficiary)
        if not schedule or schedule.revoked:
            return False
            
        # Calculate vested amount
        vested = self._get_vested_amount(schedule)
        remaining = schedule.total_amount - schedule.released_amount - vested
        
        # Transfer remaining tokens back to owner
        if remaining > 0:
            token = globals()['contracts'][self.token_address]
            if not token.transfer(self.owner, remaining):
                return False
                
        schedule.revoked = True
        return True
        
    def get_vesting_schedule(self, beneficiary: str) -> Dict:
        """Get vesting schedule details."""
        schedule = self._get_schedule(beneficiary)
        if not schedule:
            return {}
            
        return {
            'beneficiary': schedule.beneficiary,
            'total_amount': schedule.total_amount,
            'released_amount': schedule.released_amount,
            'start_time': schedule.start_time,
            'cliff_duration': schedule.cliff_duration,
            'vesting_duration': schedule.vesting_duration,
            'revoked': schedule.revoked,
            'vested_amount': self._get_vested_amount(schedule),
            'releasable_amount': self._get_releasable_amount(schedule)
        }
        
    def _get_schedule(self, beneficiary: str) -> VestingSchedule:
        """Get vesting schedule for beneficiary."""
        for schedule in self.schedules:
            if schedule.beneficiary == beneficiary:
                return schedule
        return None
        
    def _get_vested_amount(self, schedule: VestingSchedule) -> float:
        """Calculate vested amount for schedule."""
        if schedule.revoked:
            return 0
            
        current_time = globals()['block_timestamp']
        time_from_start = current_time - schedule.start_time
        
        # Check if cliff has passed
        if time_from_start < schedule.cliff_duration:
            return 0
            
        # If vesting is complete
        if time_from_start >= schedule.vesting_duration:
            return schedule.total_amount
            
        # Linear vesting
        return schedule.total_amount * time_from_start / schedule.vesting_duration
        
    def _get_releasable_amount(self, schedule: VestingSchedule) -> float:
        """Calculate releasable amount for schedule."""
        if schedule.revoked:
            return 0
            
        vested = self._get_vested_amount(schedule)
        return vested - schedule.released_amount 