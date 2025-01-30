"""
Blockchain client for interacting with the Vernachain network.
"""

from web3 import Web3
from eth_account import Account
import os
from typing import Dict, Any, Optional, List, Union
import json
import logging
from web3.middleware import geth_poa_middleware

logger = logging.getLogger(__name__)

class BlockchainClient:
    def __init__(self):
        self.node_url = os.getenv("BLOCKCHAIN_NODE_URL", "http://localhost:8545")
        self.chain_id = int(os.getenv("CHAIN_ID", "1"))
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))
        
        # Add PoA middleware if needed
        if os.getenv("USE_POA_MIDDLEWARE", "false").lower() == "true":
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABIs
        self.token_abi = self._load_abi("token")
        self.factory_abi = self._load_abi("factory")
        self.staking_abi = self._load_abi("staking")
        self.governance_abi = self._load_abi("governance")
        self.erc721_abi = self._load_abi("erc721")
        self.erc1155_abi = self._load_abi("erc1155")
        self.nft_factory_abi = self._load_abi("nft_factory")
        
        # Contract addresses
        self.factory_address = os.getenv("TOKEN_FACTORY_ADDRESS")
        self.staking_address = os.getenv("STAKING_ADDRESS")
        self.governance_address = os.getenv("GOVERNANCE_ADDRESS")
        self.nft_factory_address = os.getenv("NFT_FACTORY_ADDRESS")

    def _load_abi(self, name: str) -> Dict:
        """Load contract ABI from file"""
        try:
            with open(f"src/api/blockchain/abi/{name}.json") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {name} ABI: {e}")
            return {}

    # Token Operations
    def create_token(self, params: Dict[str, Any]) -> str:
        """Create a new token contract"""
        factory = self.web3.eth.contract(
            address=self.factory_address,
            abi=self.factory_abi
        )
        tx = factory.functions.createToken(
            params["name"],
            params["symbol"],
            params["initial_supply"],
            params["decimals"],
            params["is_mintable"],
            params["is_burnable"],
            params["is_pausable"]
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 2000000,
            'nonce': self.web3.eth.get_transaction_count(params["owner_address"])
        })
        return tx

    def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Get token information"""
        token = self.web3.eth.contract(
            address=token_address,
            abi=self.token_abi
        )
        return {
            "name": token.functions.name().call(),
            "symbol": token.functions.symbol().call(),
            "total_supply": token.functions.totalSupply().call(),
            "decimals": token.functions.decimals().call()
        }

    # Token Holder Operations
    def get_token_holders(self, token_address: str, from_block: int = 0) -> List[Dict[str, Any]]:
        """Get list of token holders from transfer events"""
        token = self.web3.eth.contract(
            address=token_address,
            abi=self.token_abi
        )
        transfer_events = token.events.Transfer.get_logs(fromBlock=from_block)
        holders = {}
        
        for event in transfer_events:
            from_addr = event["args"]["from"]
            to_addr = event["args"]["to"]
            amount = event["args"]["value"]
            
            if from_addr != "0x0000000000000000000000000000000000000000":
                if from_addr not in holders:
                    holders[from_addr] = token.functions.balanceOf(from_addr).call()
                    
            if to_addr != "0x0000000000000000000000000000000000000000":
                if to_addr not in holders:
                    holders[to_addr] = token.functions.balanceOf(to_addr).call()
        
        return [{"address": addr, "balance": bal} for addr, bal in holders.items()]

    # Staking Operations
    def stake_tokens(self, token_address: str, amount: str, staker_address: str) -> Dict[str, Any]:
        """Stake tokens"""
        staking = self.web3.eth.contract(
            address=self.staking_address,
            abi=self.staking_abi
        )
        tx = staking.functions.stake(
            token_address,
            int(amount)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(staker_address)
        })
        return tx

    def unstake_tokens(self, token_address: str, amount: str, staker_address: str) -> Dict[str, Any]:
        """Unstake tokens"""
        staking = self.web3.eth.contract(
            address=self.staking_address,
            abi=self.staking_abi
        )
        tx = staking.functions.unstake(
            token_address,
            int(amount)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(staker_address)
        })
        return tx

    def get_staking_info(self, token_address: str, staker_address: str) -> Dict[str, Any]:
        """Get staking information"""
        staking = self.web3.eth.contract(
            address=self.staking_address,
            abi=self.staking_abi
        )
        return {
            "staked_amount": staking.functions.stakedAmount(token_address, staker_address).call(),
            "rewards": staking.functions.getRewards(token_address, staker_address).call(),
            "lock_period": staking.functions.getLockPeriod(token_address).call()
        }

    # Governance Operations
    def create_proposal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a governance proposal"""
        governance = self.web3.eth.contract(
            address=self.governance_address,
            abi=self.governance_abi
        )
        tx = governance.functions.createProposal(
            params["title"],
            params["description"],
            params["targets"],
            params["values"],
            params["signatures"],
            params["calldatas"],
            params["start_block"],
            params["end_block"]
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 500000,
            'nonce': self.web3.eth.get_transaction_count(params["proposer_address"])
        })
        return tx

    def cast_vote(self, proposal_id: int, support: bool, voter_address: str) -> Dict[str, Any]:
        """Cast a vote on a proposal"""
        governance = self.web3.eth.contract(
            address=self.governance_address,
            abi=self.governance_abi
        )
        tx = governance.functions.castVote(
            proposal_id,
            support
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 100000,
            'nonce': self.web3.eth.get_transaction_count(voter_address)
        })
        return tx

    def get_proposal(self, proposal_id: int) -> Dict[str, Any]:
        """Get proposal information"""
        governance = self.web3.eth.contract(
            address=self.governance_address,
            abi=self.governance_abi
        )
        proposal = governance.functions.proposals(proposal_id).call()
        return {
            "id": proposal_id,
            "proposer": proposal[0],
            "title": proposal[1],
            "description": proposal[2],
            "start_block": proposal[3],
            "end_block": proposal[4],
            "for_votes": proposal[5],
            "against_votes": proposal[6],
            "executed": proposal[7]
        }

    # Network Operations
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            latest_block = self.web3.eth.get_block('latest')
            gas_price = self.web3.eth.gas_price
            return {
                "chain_id": self.chain_id,
                "latest_block": latest_block["number"],
                "gas_price": str(gas_price),
                "is_syncing": self.web3.eth.syncing,
                "peer_count": self.web3.net.peer_count
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {}

    def transfer_tokens(self, token_address: str, from_address: str, 
                       to_address: str, amount: str) -> str:
        """Transfer tokens"""
        token = self.web3.eth.contract(
            address=token_address,
            abi=self.token_abi
        )
        tx = token.functions.transfer(
            to_address,
            int(amount)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 100000,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        return tx

    def mint_tokens(self, token_address: str, to_address: str, 
                   amount: str, owner_address: str) -> str:
        """Mint new tokens"""
        token = self.web3.eth.contract(
            address=token_address,
            abi=self.token_abi
        )
        tx = token.functions.mint(
            to_address,
            int(amount)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 100000,
            'nonce': self.web3.eth.get_transaction_count(owner_address)
        })
        return tx

    def burn_tokens(self, token_address: str, amount: str, 
                   owner_address: str) -> str:
        """Burn tokens"""
        token = self.web3.eth.contract(
            address=token_address,
            abi=self.token_abi
        )
        tx = token.functions.burn(
            int(amount)
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 100000,
            'nonce': self.web3.eth.get_transaction_count(owner_address)
        })
        return tx

    def get_block(self, block_number: int) -> Optional[Dict[str, Any]]:
        """Get block information"""
        try:
            block = self.web3.eth.get_block(block_number, full_transactions=True)
            return dict(block)
        except Exception as e:
            logger.error(f"Failed to get block {block_number}: {e}")
            return None

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction information"""
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            return dict(tx)
        except Exception as e:
            logger.error(f"Failed to get transaction {tx_hash}: {e}")
            return None

    def get_address_info(self, address: str) -> Dict[str, Any]:
        """Get address information"""
        try:
            balance = self.web3.eth.get_balance(address)
            tx_count = self.web3.eth.get_transaction_count(address)
            return {
                "balance": str(balance),
                "transaction_count": tx_count
            }
        except Exception as e:
            logger.error(f"Failed to get address info {address}: {e}")
            return {
                "balance": "0",
                "transaction_count": 0
            }

    # NFT Operations (ERC721)
    def create_nft_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new NFT collection"""
        factory = self.web3.eth.contract(
            address=self.nft_factory_address,
            abi=self.nft_factory_abi
        )
        tx = factory.functions.createNFTCollection(
            params["name"],
            params["symbol"],
            params["base_uri"],
            params["is_burnable"],
            params["is_pausable"]
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 3000000,
            'nonce': self.web3.eth.get_transaction_count(params["owner_address"])
        })
        return tx

    def mint_nft(self, collection_address: str, to_address: str, 
                 token_id: int, uri: str, owner_address: str) -> Dict[str, Any]:
        """Mint a new NFT"""
        nft = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc721_abi
        )
        tx = nft.functions.mint(
            to_address,
            token_id,
            uri
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(owner_address)
        })
        return tx

    def get_nft_info(self, collection_address: str, token_id: int) -> Dict[str, Any]:
        """Get NFT information"""
        nft = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc721_abi
        )
        owner = nft.functions.ownerOf(token_id).call()
        uri = nft.functions.tokenURI(token_id).call()
        return {
            "token_id": token_id,
            "owner": owner,
            "uri": uri,
            "approved": nft.functions.getApproved(token_id).call()
        }

    def transfer_nft(self, collection_address: str, from_address: str,
                    to_address: str, token_id: int) -> Dict[str, Any]:
        """Transfer NFT"""
        nft = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc721_abi
        )
        tx = nft.functions.transferFrom(
            from_address,
            to_address,
            token_id
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        return tx

    # Multi-Token Operations (ERC1155)
    def create_multi_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ERC1155 token collection"""
        factory = self.web3.eth.contract(
            address=self.nft_factory_address,
            abi=self.nft_factory_abi
        )
        tx = factory.functions.createMultiToken(
            params["name"],
            params["uri"],
            params["is_burnable"],
            params["is_pausable"]
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 3000000,
            'nonce': self.web3.eth.get_transaction_count(params["owner_address"])
        })
        return tx

    def mint_multi_token(self, collection_address: str, to_address: str,
                        token_id: int, amount: int, data: bytes,
                        owner_address: str) -> Dict[str, Any]:
        """Mint ERC1155 tokens"""
        token = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc1155_abi
        )
        tx = token.functions.mint(
            to_address,
            token_id,
            amount,
            data
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(owner_address)
        })
        return tx

    def batch_mint_multi_token(self, collection_address: str, to_address: str,
                             token_ids: List[int], amounts: List[int],
                             data: bytes, owner_address: str) -> Dict[str, Any]:
        """Batch mint ERC1155 tokens"""
        token = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc1155_abi
        )
        tx = token.functions.mintBatch(
            to_address,
            token_ids,
            amounts,
            data
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 500000,
            'nonce': self.web3.eth.get_transaction_count(owner_address)
        })
        return tx

    def get_multi_token_info(self, collection_address: str,
                            token_id: int, address: str) -> Dict[str, Any]:
        """Get ERC1155 token information"""
        token = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc1155_abi
        )
        balance = token.functions.balanceOf(address, token_id).call()
        uri = token.functions.uri(token_id).call()
        return {
            "token_id": token_id,
            "balance": balance,
            "uri": uri
        }

    def transfer_multi_token(self, collection_address: str, from_address: str,
                           to_address: str, token_id: int, amount: int,
                           data: bytes) -> Dict[str, Any]:
        """Transfer ERC1155 tokens"""
        token = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc1155_abi
        )
        tx = token.functions.safeTransferFrom(
            from_address,
            to_address,
            token_id,
            amount,
            data
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 200000,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        return tx

    def batch_transfer_multi_token(self, collection_address: str,
                                 from_address: str, to_address: str,
                                 token_ids: List[int], amounts: List[int],
                                 data: bytes) -> Dict[str, Any]:
        """Batch transfer ERC1155 tokens"""
        token = self.web3.eth.contract(
            address=collection_address,
            abi=self.erc1155_abi
        )
        tx = token.functions.safeBatchTransferFrom(
            from_address,
            to_address,
            token_ids,
            amounts,
            data
        ).build_transaction({
            'chainId': self.chain_id,
            'gas': 500000,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })
        return tx

    # Token Balance Operations
    def get_token_balance(self, token_address: str, token_type: str,
                         holder_address: str, token_id: int = None) -> str:
        """Get token balance for any token type"""
        if token_type == "erc20":
            token = self.web3.eth.contract(
                address=token_address,
                abi=self.token_abi
            )
            return str(token.functions.balanceOf(holder_address).call())
        elif token_type == "erc721":
            token = self.web3.eth.contract(
                address=token_address,
                abi=self.erc721_abi
            )
            return str(token.functions.balanceOf(holder_address).call())
        elif token_type == "erc1155":
            if token_id is None:
                raise ValueError("token_id is required for ERC1155")
            token = self.web3.eth.contract(
                address=token_address,
                abi=self.erc1155_abi
            )
            return str(token.functions.balanceOf(holder_address, token_id).call())
        else:
            raise ValueError("Unsupported token type") 