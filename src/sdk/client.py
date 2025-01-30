from typing import Dict, List, Optional
from .types import Transaction, Block, SmartContract
import requests
import websockets
import json
import asyncio

class VernachainClient:
    def __init__(self, node_url: str, api_key: Optional[str] = None):
        self.node_url = node_url.rstrip('/')
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}

    # Transaction Methods
    async def create_transaction(self, sender: str, recipient: str, amount: float, 
                               shard_id: int = 0) -> Transaction:
        """Create a new transaction in the specified shard."""
        endpoint = f"{self.node_url}/api/v1/transactions"
        payload = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'shard_id': shard_id
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return Transaction(**response.json())

    async def get_transaction(self, tx_hash: str) -> Transaction:
        """Get transaction details by hash."""
        endpoint = f"{self.node_url}/api/v1/transactions/{tx_hash}"
        response = requests.get(endpoint, headers=self.headers)
        return Transaction(**response.json())

    # Block Methods
    async def get_block(self, block_number: int, shard_id: int = 0) -> Block:
        """Get block details by number and shard ID."""
        endpoint = f"{self.node_url}/api/v1/blocks/{block_number}?shard_id={shard_id}"
        response = requests.get(endpoint, headers=self.headers)
        return Block(**response.json())

    async def get_latest_block(self, shard_id: int = 0) -> Block:
        """Get the latest block in the specified shard."""
        endpoint = f"{self.node_url}/api/v1/blocks/latest?shard_id={shard_id}"
        response = requests.get(endpoint, headers=self.headers)
        return Block(**response.json())

    # Smart Contract Methods
    async def deploy_contract(self, contract_type: str, params: Dict) -> SmartContract:
        """Deploy a new smart contract."""
        endpoint = f"{self.node_url}/api/v1/contracts"
        payload = {
            'contract_type': contract_type,
            'params': params
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return SmartContract(**response.json())

    async def call_contract(self, contract_address: str, method: str, 
                          params: Dict) -> Dict:
        """Call a smart contract method."""
        endpoint = f"{self.node_url}/api/v1/contracts/{contract_address}/call"
        payload = {
            'method': method,
            'params': params
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()

    # Cross-Shard Operations
    async def initiate_cross_shard_transfer(self, from_shard: int, to_shard: int,
                                          transaction: Dict) -> str:
        """Initiate a cross-shard transfer."""
        endpoint = f"{self.node_url}/api/v1/cross-shard/transfer"
        payload = {
            'from_shard': from_shard,
            'to_shard': to_shard,
            'transaction': transaction
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()['transfer_id']

    # WebSocket Subscriptions
    async def subscribe_to_blocks(self, shard_id: int = 0):
        """Subscribe to new blocks in real-time."""
        async with websockets.connect(
            f"{self.node_url.replace('http', 'ws')}/ws/blocks?shard_id={shard_id}"
        ) as websocket:
            while True:
                block = await websocket.recv()
                yield Block(**json.loads(block))

    async def subscribe_to_transactions(self, shard_id: int = 0):
        """Subscribe to new transactions in real-time."""
        async with websockets.connect(
            f"{self.node_url.replace('http', 'ws')}/ws/transactions?shard_id={shard_id}"
        ) as websocket:
            while True:
                tx = await websocket.recv()
                yield Transaction(**json.loads(tx))

    # Validator Operations
    async def get_validator_set(self, shard_id: int = 0) -> List[Dict]:
        """Get the current validator set for a shard."""
        endpoint = f"{self.node_url}/api/v1/validators?shard_id={shard_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()['validators']

    async def stake(self, amount: float, validator_address: str) -> Dict:
        """Stake tokens for validation."""
        endpoint = f"{self.node_url}/api/v1/stake"
        payload = {
            'amount': amount,
            'validator_address': validator_address
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()

    # Bridge Operations
    async def bridge_transfer(self, target_chain: str, amount: float, 
                            recipient: str) -> str:
        """Initiate a cross-chain bridge transfer."""
        endpoint = f"{self.node_url}/api/v1/bridge/transfer"
        payload = {
            'target_chain': target_chain,
            'amount': amount,
            'recipient': recipient
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()['transfer_id'] 