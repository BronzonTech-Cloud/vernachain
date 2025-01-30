"""
Governance service for managing DAO operations.
"""

from typing import Dict, Any, List, Optional
import logging
from ..database import SessionLocal, DBToken, DBTransaction
from ..blockchain.client import BlockchainClient
from datetime import datetime, timedelta
from sqlalchemy import and_
import json

logger = logging.getLogger(__name__)

class GovernanceService:
    def __init__(self):
        self.blockchain = BlockchainClient()

    def create_proposal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new governance proposal"""
        try:
            # Validate proposal parameters
            self._validate_proposal(params)
            
            # Create proposal transaction
            tx = self.blockchain.create_proposal({
                "title": params["title"],
                "description": params["description"],
                "targets": params["targets"],
                "values": params["values"],
                "signatures": params["signatures"],
                "calldatas": params["calldatas"],
                "start_block": params["start_block"],
                "end_block": params["end_block"],
                "proposer_address": params["proposer_address"]
            })
            
            return {
                "transaction": tx,
                "message": "Proposal creation submitted"
            }
        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            raise

    def get_proposal_details(self, proposal_id: int) -> Dict[str, Any]:
        """Get comprehensive proposal details"""
        try:
            # Get on-chain proposal data
            proposal = self.blockchain.get_proposal(proposal_id)
            
            # Get voting stats
            stats = self._get_voting_stats(proposal_id)
            
            # Get execution status
            execution_status = self._get_execution_status(proposal_id)
            
            return {
                **proposal,
                "voting_stats": stats,
                "execution_status": execution_status,
                "timeline": self._get_proposal_timeline(proposal)
            }
        except Exception as e:
            logger.error(f"Error getting proposal details: {e}")
            raise

    def cast_vote(self, proposal_id: int, voter_address: str,
                 support: bool, reason: str = "") -> Dict[str, Any]:
        """Cast a vote on a proposal"""
        try:
            # Check voting eligibility
            self._check_voting_eligibility(proposal_id, voter_address)
            
            # Cast vote transaction
            tx = self.blockchain.cast_vote(proposal_id, support, voter_address)
            
            return {
                "transaction": tx,
                "message": "Vote submitted successfully"
            }
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            raise

    def delegate_votes(self, token_address: str, delegator_address: str,
                      delegate_address: str) -> Dict[str, Any]:
        """Delegate voting power"""
        try:
            tx = self.blockchain.delegate_votes(
                token_address,
                delegator_address,
                delegate_address
            )
            
            return {
                "transaction": tx,
                "message": "Delegation submitted successfully"
            }
        except Exception as e:
            logger.error(f"Error delegating votes: {e}")
            raise

    def get_voting_power(self, token_address: str, voter_address: str,
                        block_number: Optional[int] = None) -> str:
        """Get voting power of an address"""
        try:
            return self.blockchain.get_voting_power(
                token_address,
                voter_address,
                block_number
            )
        except Exception as e:
            logger.error(f"Error getting voting power: {e}")
            raise

    def queue_proposal(self, proposal_id: int, executor_address: str) -> Dict[str, Any]:
        """Queue a successful proposal for execution"""
        try:
            tx = self.blockchain.queue_proposal(proposal_id, executor_address)
            return {
                "transaction": tx,
                "message": "Proposal queued for execution"
            }
        except Exception as e:
            logger.error(f"Error queueing proposal: {e}")
            raise

    def execute_proposal(self, proposal_id: int, executor_address: str) -> Dict[str, Any]:
        """Execute a queued proposal"""
        try:
            tx = self.blockchain.execute_proposal(proposal_id, executor_address)
            return {
                "transaction": tx,
                "message": "Proposal execution submitted"
            }
        except Exception as e:
            logger.error(f"Error executing proposal: {e}")
            raise

    def get_governance_strategy(self) -> Dict[str, Any]:
        """Get current governance strategy parameters"""
        try:
            return self.blockchain.get_governance_strategy()
        except Exception as e:
            logger.error(f"Error getting governance strategy: {e}")
            raise

    def _validate_proposal(self, params: Dict[str, Any]):
        """Validate proposal parameters"""
        required_fields = [
            "title", "description", "targets", "values",
            "signatures", "calldatas", "start_block", "end_block"
        ]
        
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")
                
        if len(params["targets"]) != len(params["values"]) or \
           len(params["targets"]) != len(params["signatures"]) or \
           len(params["targets"]) != len(params["calldatas"]):
            raise ValueError("Mismatched array lengths in proposal parameters")
            
        if params["start_block"] >= params["end_block"]:
            raise ValueError("End block must be greater than start block")

    def _get_voting_stats(self, proposal_id: int) -> Dict[str, Any]:
        """Get detailed voting statistics"""
        try:
            votes = self.blockchain.get_proposal_votes(proposal_id)
            total_votes = votes["for_votes"] + votes["against_votes"]
            
            return {
                "total_votes": total_votes,
                "for_votes": votes["for_votes"],
                "against_votes": votes["against_votes"],
                "for_percentage": (votes["for_votes"] / total_votes * 100) if total_votes > 0 else 0,
                "against_percentage": (votes["against_votes"] / total_votes * 100) if total_votes > 0 else 0,
                "quorum_reached": self._check_quorum(votes["for_votes"] + votes["against_votes"]),
                "vote_differential": votes["for_votes"] - votes["against_votes"]
            }
        except Exception as e:
            logger.error(f"Error getting voting stats: {e}")
            return {}

    def _get_execution_status(self, proposal_id: int) -> Dict[str, Any]:
        """Get proposal execution status"""
        try:
            status = self.blockchain.get_proposal_state(proposal_id)
            timeline = self.blockchain.get_proposal_timeline(proposal_id)
            
            return {
                "state": status,
                "queued_at": timeline.get("queued_at"),
                "executed_at": timeline.get("executed_at"),
                "cancelable": self._is_proposal_cancelable(proposal_id),
                "executable": self._is_proposal_executable(proposal_id)
            }
        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return {}

    def _get_proposal_timeline(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proposal timeline"""
        return {
            "created_at": proposal.get("created_at"),
            "voting_starts": self._block_to_timestamp(proposal["start_block"]),
            "voting_ends": self._block_to_timestamp(proposal["end_block"]),
            "queued_at": proposal.get("queued_at"),
            "executed_at": proposal.get("executed_at")
        }

    def _check_voting_eligibility(self, proposal_id: int, voter_address: str):
        """Check if address can vote on proposal"""
        proposal = self.blockchain.get_proposal(proposal_id)
        current_block = self.blockchain.web3.eth.block_number
        
        if current_block < proposal["start_block"]:
            raise ValueError("Voting has not started yet")
            
        if current_block > proposal["end_block"]:
            raise ValueError("Voting has ended")
            
        voting_power = self.get_voting_power(
            self.blockchain.governance_token_address,
            voter_address,
            proposal["start_block"]
        )
        
        if int(voting_power) == 0:
            raise ValueError("No voting power at proposal start")

    def _check_quorum(self, total_votes: int) -> bool:
        """Check if proposal has reached quorum"""
        try:
            quorum = self.blockchain.get_quorum()
            return total_votes >= int(quorum)
        except Exception as e:
            logger.error(f"Error checking quorum: {e}")
            return False

    def _block_to_timestamp(self, block_number: int) -> int:
        """Convert block number to estimated timestamp"""
        try:
            current_block = self.blockchain.web3.eth.block_number
            current_block_data = self.blockchain.web3.eth.get_block(current_block)
            avg_block_time = 15  # seconds
            
            block_difference = block_number - current_block
            time_difference = block_difference * avg_block_time
            
            return current_block_data["timestamp"] + time_difference
        except Exception as e:
            logger.error(f"Error converting block to timestamp: {e}")
            return 0

    def _is_proposal_cancelable(self, proposal_id: int) -> bool:
        """Check if proposal can be canceled"""
        try:
            return self.blockchain.can_cancel_proposal(proposal_id)
        except Exception as e:
            logger.error(f"Error checking if proposal is cancelable: {e}")
            return False

    def _is_proposal_executable(self, proposal_id: int) -> bool:
        """Check if proposal can be executed"""
        try:
            return self.blockchain.can_execute_proposal(proposal_id)
        except Exception as e:
            logger.error(f"Error checking if proposal is executable: {e}")
            return False 