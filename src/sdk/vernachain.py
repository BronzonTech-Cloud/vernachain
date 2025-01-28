from typing import Dict, List, Optional, Any
import json
import asyncio
from ..networking.node import Node
from ..wallet.wallet import Wallet
from ..blockchain.smart_contracts.vm import SmartContractVM

class VernachainSDK:
    """Python SDK for interacting with Vernachain."""
    
    def __init__(self, node_host: str = 'localhost', node_port: int = 5000):
        self.node = Node(node_host, node_port)
        self.wallet = Wallet()
        self.contract_vm = SmartContractVM()
        
    async def connect(self) -> bool:
        """Connect to the node asynchronously."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, self.node.start)
            return True
        except Exception as e:
            return False
        
    async def disconnect(self):
        """Disconnect from the network."""
        await self.node.stop()
        
    # Wallet operations
    def create_wallet(self, label: str = "") -> str:
        """Create a new wallet address."""
        return self.wallet.create_address(label)
        
    async def get_balance(self, address: str) -> float:
        """Get balance for an address asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.node.blockchain.get_balance, address
        )
        
    def get_stake(self, address: str) -> float:
        """Get staked amount for an address."""
        return self.wallet.get_stake(address)
        
    def list_wallets(self) -> List[Dict]:
        """List all wallet addresses."""
        return self.wallet.list_addresses()
        
    # Transaction operations
    async def send_transaction(self, to_address: str, amount: float) -> Optional[str]:
        """Send a transaction asynchronously."""
        transaction = self.wallet.create_transaction(to_address, amount)
        await asyncio.get_event_loop().run_in_executor(
            None, self.node.broadcast_transaction, transaction
        )
        return transaction.hash
        
    async def stake_tokens(self, address: str, amount: float) -> Dict:
        """Stake tokens for PoS."""
        tx = self.wallet.stake_tokens(address, amount)
        await self.node.broadcast_transaction(tx)
        return tx
        
    async def unstake_tokens(self, address: str, amount: float) -> Dict:
        """Unstake tokens from PoS."""
        tx = self.wallet.unstake_tokens(address, amount)
        await self.node.broadcast_transaction(tx)
        return tx
        
    # Smart contract operations
    async def deploy_contract(self, from_address: str, code: str,
                            constructor_args: List[Any] = None) -> str:
        """Deploy a smart contract."""
        # Compile and validate contract code
        contract_bytecode = self.contract_vm.compile(code)
        
        # Create deployment transaction
        tx = self.wallet.create_transaction(
            from_address,
            "0x0",  # Contract creation address
            0,  # No value transfer
            json.dumps({
                "type": "contract_deploy",
                "bytecode": contract_bytecode,
                "args": constructor_args or []
            })
        )
        
        # Broadcast transaction
        await self.node.broadcast_transaction(tx)
        
        # Return contract address (derived from transaction hash)
        return f"0x{tx['signature'][:40]}"  # First 20 bytes of signature
        
    async def call_contract(self, contract_address: str, from_address: str,
                          function_name: str, args: List[Any] = None,
                          value: float = 0) -> Any:
        """Call a contract function."""
        tx = self.wallet.create_transaction(
            from_address,
            contract_address,
            value,
            json.dumps({
                "type": "contract_call",
                "function": function_name,
                "args": args or []
            })
        )
        
        # Broadcast transaction
        await self.node.broadcast_transaction(tx)
        
        # Wait for transaction execution and return result
        result = await self.node.wait_for_transaction(tx['signature'])
        return result.get("return_value")
        
    async def get_contract_state(self, contract_address: str) -> Dict:
        """Get current state of a contract."""
        return await self.node.get_contract_state(contract_address)
        
    # Blockchain queries
    async def get_block(self, block_number: Optional[int] = None) -> Dict:
        """Get block information."""
        return await self.node.get_block(block_number)
        
    async def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction information."""
        return await self.node.get_transaction(tx_hash)
        
    async def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt."""
        return await self.node.get_transaction_receipt(tx_hash)
        
    # Network operations
    def get_network_stats(self) -> Dict:
        """Get network statistics."""
        return self.node.get_network_stats()
        
    async def subscribe_to_events(self, event_type: str, callback: callable):
        """Subscribe to blockchain events."""
        await self.node.subscribe_to_events(event_type, callback)
        
    async def unsubscribe_from_events(self, event_type: str, callback: callable):
        """Unsubscribe from blockchain events."""
        await self.node.unsubscribe_from_events(event_type, callback) 