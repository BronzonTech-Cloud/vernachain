"""Governance contract for token governance features."""

from typing import Dict, List
from enum import Enum
from datetime import datetime

class ProposalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class Proposal:
    def __init__(self, id: int, creator: str, description: str, actions: List[Dict]):
        self.id = id
        self.creator = creator
        self.description = description
        self.actions = actions
        self.for_votes = 0.0
        self.against_votes = 0.0
        self.status = ProposalStatus.PENDING
        self.start_time = 0
        self.end_time = 0
        self.executed = False
        self.voters = {}  # address -> vote weight

class GovernanceContract:
    """Contract for token governance."""
    
    def __init__(self, token_address: str, voting_delay: int = 1, voting_period: int = 3 * 24 * 3600):
        """
        Initialize governance contract.
        
        Args:
            token_address: Address of governance token
            voting_delay: Blocks before voting starts
            voting_period: Voting duration in seconds
        """
        self.token_address = token_address
        self.voting_delay = voting_delay
        self.voting_period = voting_period
        self.proposal_count = 0
        self.proposals = {}  # id -> Proposal
        self.quorum = 0.04  # 4% of total supply needed
        self.owner = globals()['sender']
        
    def propose(self, description: str, actions: List[Dict]) -> int:
        """Create a new proposal."""
        token = globals()['contracts'][self.token_address]
        proposer_balance = token.balance_of(globals()['sender'])
        
        # Check if proposer has enough tokens
        if proposer_balance < (token.total_supply * 0.01):  # 1% of total supply
            return 0
            
        self.proposal_count += 1
        proposal = Proposal(
            id=self.proposal_count,
            creator=globals()['sender'],
            description=description,
            actions=actions
        )
        
        proposal.start_time = globals()['block_timestamp'] + self.voting_delay
        proposal.end_time = proposal.start_time + self.voting_period
        proposal.status = ProposalStatus.PENDING
        
        self.proposals[proposal.id] = proposal
        return proposal.id
        
    def cast_vote(self, proposal_id: int, support: bool) -> bool:
        """Cast vote on proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
            
        # Check if proposal is active
        current_time = globals()['block_timestamp']
        if current_time < proposal.start_time or current_time > proposal.end_time:
            return False
            
        if proposal.status != ProposalStatus.ACTIVE:
            if proposal.status == ProposalStatus.PENDING and current_time >= proposal.start_time:
                proposal.status = ProposalStatus.ACTIVE
            else:
                return False
                
        # Get voter's voting power (token balance)
        token = globals()['contracts'][self.token_address]
        vote_weight = token.balance_of(globals()['sender'])
        
        # Remove previous vote if exists
        if globals()['sender'] in proposal.voters:
            old_weight = proposal.voters[globals()['sender']]
            if support:
                proposal.for_votes -= old_weight
            else:
                proposal.against_votes -= old_weight
                
        # Record new vote
        proposal.voters[globals()['sender']] = vote_weight
        if support:
            proposal.for_votes += vote_weight
        else:
            proposal.against_votes += vote_weight
            
        return True
        
    def execute_proposal(self, proposal_id: int) -> bool:
        """Execute a successful proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
            
        # Check if proposal can be executed
        if proposal.status != ProposalStatus.SUCCEEDED:
            if proposal.status == ProposalStatus.ACTIVE and globals()['block_timestamp'] > proposal.end_time:
                self._update_proposal_status(proposal)
            if proposal.status != ProposalStatus.SUCCEEDED:
                return False
                
        # Execute actions
        for action in proposal.actions:
            contract = globals()['contracts'][action['target']]
            method = getattr(contract, action['function'])
            method(*action['args'])
            
        proposal.status = ProposalStatus.EXECUTED
        proposal.executed = True
        return True
        
    def _update_proposal_status(self, proposal: Proposal) -> None:
        """Update proposal status based on votes."""
        if proposal.status != ProposalStatus.ACTIVE:
            return
            
        token = globals()['contracts'][self.token_address]
        total_supply = token.total_supply
        
        # Check if quorum reached
        if (proposal.for_votes + proposal.against_votes) / total_supply < self.quorum:
            proposal.status = ProposalStatus.DEFEATED
            return
            
        # Check if proposal succeeded
        if proposal.for_votes > proposal.against_votes:
            proposal.status = ProposalStatus.SUCCEEDED
        else:
            proposal.status = ProposalStatus.DEFEATED
            
    def get_proposal(self, proposal_id: int) -> Dict:
        """Get proposal details."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {}
            
        return {
            'id': proposal.id,
            'creator': proposal.creator,
            'description': proposal.description,
            'actions': proposal.actions,
            'for_votes': proposal.for_votes,
            'against_votes': proposal.against_votes,
            'status': proposal.status.value,
            'start_time': proposal.start_time,
            'end_time': proposal.end_time,
            'executed': proposal.executed
        } 