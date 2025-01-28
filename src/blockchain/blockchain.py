import json
import hashlib
from time import time
from typing import List, Dict, Any, Optional, Set
from .block import Block
from .transaction import Transaction
from .transaction_pool import TransactionPool
from .consensus import ProofOfStake, Validator
from .sharding import MasterChain, ShardChain, CrossShardMessage
from src.blockchain.smart_contracts.vm import SmartContractVM
from datetime import datetime

from src.utils.crypto import hash_data, generate_merkle_root, verify_signature
from src.utils.validation import is_valid_transaction, is_valid_block, is_valid_stake_amount
from src.utils.serialization import serialize_block, serialize_transaction
from src.utils.logging import blockchain_logger
from ..consensus.validator_manager import ValidatorManager


class Blockchain:
    def __init__(self, num_shards: int = 4, block_reward: float = 10.0):
        """
        Initialize a new blockchain with sharding support.
        
        Args:
            num_shards: Number of shards to create
            block_reward: Reward for producing a block
        """
        self.master_chain = MasterChain(num_shards)
        self.shard_chains: Dict[int, ShardChain] = {}
        self.transaction_pool = TransactionPool()
        self.consensus = ProofOfStake()
        self.block_reward = block_reward
        self.vm = SmartContractVM()
        
        # Initialize shard chains
        for i in range(num_shards):
            self.shard_chains[i] = ShardChain(i)
            
        self.create_genesis_blocks()
        blockchain_logger.info("Blockchain initialized with genesis blocks")

        self.chain: List[Dict] = []
        self.pending_transactions: List[Dict] = []
        self.validator_manager = ValidatorManager()
        self.create_genesis_block()

    def create_genesis_blocks(self) -> None:
        """Create genesis blocks for master chain and all shards."""
        # Create master chain genesis block
        master_genesis = Block(
            index=0,
            transactions=[],
            timestamp=time(),
            previous_hash="0" * 64,
            validator="0"  # System address
        )
        self.master_chain.chain.append(master_genesis)
        
        # Create genesis blocks for each shard
        for shard_chain in self.shard_chains.values():
            shard_genesis = Block(
                index=0,
                transactions=[],
                timestamp=time(),
                previous_hash="0" * 64,
                validator="0"  # System address
            )
            shard_chain.chain.append(shard_genesis)

    def register_validator(self, address: str, stake_amount: float) -> bool:
        """Register a new validator."""
        return self.validator_manager.register_validator(address, stake_amount)

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a new transaction to the appropriate shard's transaction pool.
        
        Args:
            transaction: Transaction to add
            
        Returns:
            bool: True if transaction was added successfully
        """
        # Determine which shard should process this transaction
        sender_shard = self.master_chain.get_shard_for_address(transaction.sender)
        receiver_shard = self.master_chain.get_shard_for_address(transaction.receiver)
        
        if sender_shard == receiver_shard:
            # Intra-shard transaction
            return self.transaction_pool.add_transaction(transaction)
        else:
            # Cross-shard transaction
            tx_hash = transaction.calculate_hash()
            merkle_proof = self._create_merkle_proof(sender_shard, tx_hash)
            
            # Create cross-shard message
            message_hash = self.master_chain.create_cross_shard_message(
                sender_shard,
                receiver_shard,
                tx_hash,
                merkle_proof
            )
            
            if message_hash:
                self.shard_chains[sender_shard].pending_messages.append(
                    self.master_chain.cross_shard_messages[message_hash]
                )
                return True
                
        return False

    def _create_merkle_proof(self, shard_id: int, tx_hash: str) -> List[str]:
        """Create a Merkle proof for a transaction in a shard."""
        shard_chain = self.shard_chains[shard_id]
        state_items = []
        
        for block in shard_chain.chain:
            for tx in block.transactions:
                state_items.append(json.dumps(tx, sort_keys=True))
                
        # Find position of transaction in state
        tx_pos = -1
        for i, item in enumerate(state_items):
            if hashlib.sha256(item.encode()).hexdigest() == tx_hash:
                tx_pos = i
                break
                
        if tx_pos == -1:
            return []
            
        # Build Merkle proof
        proof = []
        current_pos = tx_pos
        hashes = [hashlib.sha256(item.encode()).hexdigest() for item in state_items]
        
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
                
            proof_element = hashes[current_pos ^ 1]  # Get sibling hash
            proof.append(proof_element)
            
            # Move to next level
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(next_hash)
                
            hashes = next_level
            current_pos //= 2
            
        return proof

    def create_block(self, validator_address: str) -> Optional[Block]:
        """
        Create a new block in the appropriate shard if validator is selected.
        
        Args:
            validator_address: Address of the validator
            
        Returns:
            Block if created successfully, None otherwise
        """
        # Check if address is a validator
        validator = self.consensus.validators.get(validator_address)
        if not validator or not validator.is_active:
            return None
            
        # Determine validator's shard
        validator_shard = -1
        for shard_id, shard_info in self.master_chain.shards.items():
            if validator_address in shard_info.validator_set:
                validator_shard = shard_id
                break
                
        if validator_shard == -1:
            return None
            
        # Check if validator is selected for this block
        selected_validator = self.consensus.select_validator()
        if not selected_validator or selected_validator.address != validator_address:
            self.consensus.record_block_production(validator_address, False)
            return None
            
        # Get pending transactions for this shard
        transactions = [
            tx for tx in self.transaction_pool.get_transactions()
            if self.master_chain.get_shard_for_address(tx.sender) == validator_shard
        ]
        
        # Process cross-shard messages
        shard_chain = self.shard_chains[validator_shard]
        for message in shard_chain.pending_messages:
            if self.master_chain.verify_cross_shard_message(message.transaction_hash):
                # Add cross-shard transaction
                transactions.append(Transaction.from_dict({
                    "sender": "cross_shard",
                    "receiver": message.to_shard,
                    "amount": 0.0  # Amount handled in original shard
                }))
                shard_chain.processed_messages[message.transaction_hash] = message
                
        # Create new block
        new_block = Block(
            index=len(shard_chain.chain),
            transactions=[t.to_dict() for t in transactions],
            timestamp=time(),
            previous_hash=shard_chain.chain[-1].hash,
            validator=validator_address
        )
        
        # Add block to shard chain
        if shard_chain.add_block(new_block):
            # Update master chain with new shard state
            self.master_chain.update_shard_info(
                validator_shard,
                shard_chain.get_state_root(),
                len(shard_chain.chain)
            )
            
            # Clear processed transactions and messages
            self.transaction_pool.remove_transactions(transactions)
            shard_chain.pending_messages = [
                msg for msg in shard_chain.pending_messages
                if msg.transaction_hash not in shard_chain.processed_messages
            ]
            
            self.consensus.record_block_production(validator_address, True)
            return new_block
            
        self.consensus.record_block_production(validator_address, False)
        return None

    def stake_tokens(self, address: str, amount: float) -> bool:
        """
        Stake tokens to become a validator.
        
        Args:
            address: Address of the validator
            amount: Amount to stake
            
        Returns:
            bool: True if stake was successful
        """
        # Check if address has enough balance
        balance = self.get_balance(address)
        if balance < amount:
            return False
            
        # Add or update validator
        return self.consensus.add_validator(address, amount)

    def unstake_tokens(self, address: str) -> bool:
        """
        Remove stake and validator status.
        
        Args:
            address: Address of the validator
            
        Returns:
            bool: True if unstake was successful
        """
        return self.consensus.remove_validator(address)

    def add_block(self, block: Block) -> bool:
        """
        Add a new block to the chain if it's valid.
        
        Args:
            block: Block to add to the chain
            
        Returns:
            bool: True if block was added successfully
        """
        if not self.is_valid_block(block):
            return False

        self.chain.append(block)
        return True

    def is_valid_block(self, block: Block) -> bool:
        """
        Check if a block is valid.
        
        Args:
            block: Block to validate
            
        Returns:
            bool: True if block is valid
        """
        # Check block index
        if block.index != len(self.chain):
            return False

        # Check previous hash
        if block.previous_hash != self.get_latest_block().hash:
            return False

        # Check if validator exists and is active
        validator = self.consensus.validators.get(block.validator)
        if not validator or not validator.is_active:
            return False

        # Verify block hash
        if block.hash != block.calculate_hash():
            return False

        return True

    def is_valid_chain(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            bool: True if the chain is valid
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verify block hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify block linkage
            if current_block.previous_hash != previous_block.hash:
                return False

            # Verify validator
            validator = self.consensus.validators.get(current_block.validator)
            if not validator and current_block.index > 0:  # Skip genesis block
                return False

        return True

    def get_latest_block(self) -> Block:
        """
        Get the most recent block in the chain.
        
        Returns:
            Block: The latest block
        """
        return self.chain[-1]

    def get_balance(self, address: str) -> float:
        """
        Calculate the balance of an address across all shards.
        
        Args:
            address: Address to check balance for
            
        Returns:
            float: Current balance
        """
        balance = 0.0
        address_shard = self.master_chain.get_shard_for_address(address)
        
        # Check transactions in address's primary shard
        shard_chain = self.shard_chains[address_shard]
        for block in shard_chain.chain:
            for transaction in block.transactions:
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
                if transaction["receiver"] == address:
                    balance += transaction["amount"]
                    
        # Check cross-shard transactions in other shards
        for shard_id, shard_chain in self.shard_chains.items():
            if shard_id == address_shard:
                continue
                
            for block in shard_chain.chain:
                for transaction in block.transactions:
                    if transaction["sender"] == "cross_shard" and transaction["receiver"] == address:
                        balance += transaction["amount"]
                        
        # Subtract staked amount if address is a validator
        validator = self.consensus.validators.get(address)
        if validator:
            balance -= validator.stake
            
        # Add contract balance if address is a contract
        contract_balance = self.vm.get_contract_balance(address)
        balance += contract_balance
            
        return balance

    def get_validator_info(self, address: str) -> Optional[Dict]:
        """
        Get information about a validator.
        
        Args:
            address: Validator's address
            
        Returns:
            Dict containing validator information if found
        """
        return self.consensus.get_validator_info(address)

    def get_active_validators(self) -> List[Dict]:
        """
        Get list of active validators.
        
        Returns:
            List of validator information dictionaries
        """
        return self.consensus.get_active_validators()

    def assign_validator_to_shard(self, validator_address: str) -> bool:
        """
        Assign a validator to a shard based on load balancing.
        
        Args:
            validator_address: Address of the validator
            
        Returns:
            bool: True if assignment was successful
        """
        if validator_address not in self.consensus.validators:
            return False
            
        # Find shard with fewest validators
        min_validators = float('inf')
        target_shard = 0
        
        for shard_id, shard_info in self.master_chain.shards.items():
            num_validators = len(shard_info.validator_set)
            if num_validators < min_validators:
                min_validators = num_validators
                target_shard = shard_id
                
        return self.master_chain.assign_validator_to_shard(
            validator_address,
            target_shard
        )

    def get_shard_info(self, shard_id: int) -> Optional[Dict]:
        """
        Get information about a specific shard.
        
        Args:
            shard_id: ID of the shard
            
        Returns:
            Dict containing shard information if found
        """
        if shard_id not in self.master_chain.shards:
            return None
            
        shard_info = self.master_chain.shards[shard_id]
        shard_chain = self.shard_chains[shard_id]
        
        return {
            "shard_id": shard_id,
            "validators": list(shard_info.validator_set),
            "state_root": shard_info.state_root,
            "block_height": shard_info.last_block_height,
            "pending_messages": len(shard_chain.pending_messages),
            "processed_messages": len(shard_chain.processed_messages)
        }

    def get_all_shard_info(self) -> List[Dict]:
        """
        Get information about all shards.
        
        Returns:
            List of shard information dictionaries
        """
        return [
            self.get_shard_info(shard_id)
            for shard_id in self.master_chain.shards
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the blockchain to a dictionary representation.
        
        Returns:
            Dict containing the blockchain's data
        """
        return {
            "chain": [block.to_dict() for block in self.chain],
            "transaction_pool": self.transaction_pool.to_dict(),
            "validators": [
                self.get_validator_info(addr)
                for addr in self.consensus.validators
            ]
        }

    @staticmethod
    def from_dict(chain_dict: Dict[str, Any]) -> 'Blockchain':
        """
        Create a Blockchain instance from a dictionary representation.
        
        Args:
            chain_dict: Dictionary containing blockchain data
            
        Returns:
            Blockchain: A new Blockchain instance
        """
        blockchain = Blockchain()
        blockchain.chain = [Block.from_dict(block_dict) for block_dict in chain_dict["chain"]]
        blockchain.transaction_pool = TransactionPool.from_dict(chain_dict["transaction_pool"])
        
        # Restore validators
        for validator_info in chain_dict["validators"]:
            blockchain.consensus.add_validator(
                validator_info["address"],
                validator_info["stake"]
            )
            
        return blockchain

    def deploy_contract(self, code: str, constructor_args: List[Any] = None,
                       sender: str = None, value: float = 0.0) -> Optional[str]:
        """
        Deploy a new smart contract.
        
        Args:
            code: Contract source code
            constructor_args: Arguments for the constructor
            sender: Address deploying the contract
            value: Amount to send with deployment
            
        Returns:
            str: Contract address if deployment successful
        """
        # Check sender's balance
        if value > 0:
            balance = self.get_balance(sender)
            if balance < value:
                return None
                
        # Deploy contract
        address = self.vm.deploy_contract(code, constructor_args)
        if not address:
            return None
            
        # Transfer initial value if any
        if value > 0:
            self.vm.transfer_to_contract(address, value)
            
            # Create transaction for the transfer
            transaction = Transaction(sender, address, value)
            self.add_transaction(transaction)
            
        return address

    def call_contract(self, address: str, function: str, args: List[Any] = None,
                     sender: str = None, value: float = 0.0) -> Any:
        """
        Call a smart contract function.
        
        Args:
            address: Contract address
            function: Function name to call
            args: Function arguments
            sender: Caller's address
            value: Amount to send with call
            
        Returns:
            Any: Function result
        """
        # Check sender's balance
        if value > 0:
            balance = self.get_balance(sender)
            if balance < value:
                raise Exception("Insufficient balance")
                
        # Call contract function
        result = self.vm.call_contract(address, function, args, sender, value)
        
        # Create transaction for value transfer if any
        if value > 0:
            transaction = Transaction(sender, address, value)
            self.add_transaction(transaction)
            
        return result

    def get_contract_state(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a contract.
        
        Args:
            address: Contract address
            
        Returns:
            Dict containing contract state if found
        """
        return self.vm.get_contract_state(address)

    def create_genesis_block(self) -> None:
        """Create and add the genesis block."""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now(),
            'transactions': [],
            'previous_hash': '0' * 64,
            'validator': None,
            'signature': None
        }
        genesis_block['hash'] = self._calculate_block_hash(genesis_block)
        self.chain.append(genesis_block)
        
    def _calculate_block_hash(self, block: Dict) -> str:
        """Calculate hash of a block."""
        block_content = {
            'index': block['index'],
            'timestamp': block['timestamp'].isoformat(),
            'transactions': block['transactions'],
            'previous_hash': block['previous_hash'],
            'validator': block['validator']
        }
        return hash_data(str(block_content))
        
    def create_block(self, validator_address: str) -> Dict[str, Any]:
        """Create a new block with pending transactions."""
        if validator_address not in self.validator_manager.get_validator_set():
            return None
            
        latest_block = self.get_latest_block()
        
        new_block = {
            'index': latest_block['index'] + 1,
            'timestamp': datetime.now(),
            'transactions': self.pending_transactions.copy(),
            'previous_hash': latest_block['hash'],
            'validator': validator_address,
            'merkle_root': generate_merkle_root([tx['hash'] for tx in self.pending_transactions])
        }
        
        new_block['hash'] = self._calculate_block_hash(new_block)
        return new_block
        
    def add_block(self, block: Dict, signature: bytes) -> bool:
        """Add a new block to the chain."""
        if not self._is_valid_block(block, signature):
            return False
            
        # Update validator reputation and calculate rewards
        self.validator_manager.update_reputation(
            block['validator'],
            block['index'],
            'block_proposed'
        )
        
        reward = self.validator_manager.calculate_rewards(
            block['validator'],
            block['index']
        )
        
        # Add reward transaction
        if reward > 0:
            reward_tx = {
                'from': None,  # System reward
                'to': block['validator'],
                'value': reward,
                'timestamp': datetime.now(),
                'type': 'reward'
            }
            block['transactions'].append(reward_tx)
        
        self.chain.append(block)
        self.pending_transactions = []
        return True
        
    def _is_valid_block(self, block: Dict, signature: bytes) -> bool:
        """Validate a block and its signature."""
        if block['index'] != len(self.chain):
            return False
            
        if block['previous_hash'] != self.get_latest_block()['hash']:
            return False
            
        if block['validator'] not in self.validator_manager.get_validator_set():
            return False
            
        # Verify block signature
        if not verify_signature(block['validator'], block['hash'], signature):
            self.validator_manager.update_reputation(
                block['validator'],
                block['index'],
                'invalid_block'
            )
            return False
        
        return True
        
    def _is_valid_transaction(self, transaction: Dict) -> bool:
        """Validate a transaction."""
        if transaction.get('type') == 'reward':
            return True
            
        if transaction['value'] <= 0:
            return False
            
        if transaction['from'] == transaction['to']:
            return False
            
        sender_balance = self.get_balance(transaction['from'])
        if sender_balance < transaction['value']:
            return False
            
        return True
        
    def get_validator_stats(self, address: str) -> Optional[Dict]:
        """Get statistics for a validator."""
        stats = self.validator_manager.get_validator_stats(address)
        if stats:
            return {
                'stake': stats.total_stake,
                'reputation': stats.reputation_score,
                'blocks_proposed': stats.blocks_proposed,
                'uptime': self.validator_manager._calculate_uptime(stats),
                'is_jailed': address in self.validator_manager.jailed_validators
            }
        return None 