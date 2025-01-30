from typing import Dict, List, Optional
from .types import (
    Transaction, 
    Block, 
    SmartContract, 
    Validator, 
    CrossShardTransfer, 
    BridgeTransfer
)
import aiohttp
import websockets
import json
import asyncio
from datetime import datetime

class VernachainError(Exception):
    """Base exception for Vernachain SDK."""
    pass

class ValidationError(VernachainError):
    """Raised when input validation fails."""
    pass

class NetworkError(VernachainError):
    """Raised when network operations fail."""
    pass

class AuthenticationError(VernachainError):
    """Raised when authentication fails."""
    pass

class VernachainClient:
    def __init__(self, node_url: str, api_key: Optional[str] = None):
        """Initialize the Vernachain client.
        
        Args:
            node_url: Base URL of the Vernachain node
            api_key: Optional API key for authentication
        """
        self.node_url = node_url.rstrip('/')
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make an HTTP request to the API."""
        if not self._session:
            self._session = aiohttp.ClientSession(headers=self.headers)
        
        url = f"{self.node_url}{endpoint}"
        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                if response.status >= 400:
                    error_data = await response.json()
                    raise NetworkError(f"API request failed: {error_data.get('message', 'Unknown error')}")
                return await response.json()
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network request failed: {str(e)}")

    # Transaction Methods
    async def create_transaction(self, sender: str, recipient: str, amount: float, 
                               shard_id: int = 0) -> Transaction:
        """Create a new transaction in the specified shard."""
        data = await self._request('POST', '/api/v1/transactions', json={
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'shard_id': shard_id
        })
        return Transaction(**data)

    async def get_transaction(self, tx_hash: str) -> Transaction:
        """Get transaction details by hash."""
        data = await self._request('GET', f'/api/v1/transactions/{tx_hash}')
        return Transaction(**data)

    # Block Methods
    async def get_block(self, block_number: int, shard_id: int = 0) -> Block:
        """Get block details by number and shard ID."""
        data = await self._request('GET', 
            f'/api/v1/blocks/{block_number}?shard_id={shard_id}')
        return Block(**data)

    async def get_latest_block(self, shard_id: int = 0) -> Block:
        """Get the latest block in the specified shard."""
        data = await self._request('GET', f'/api/v1/blocks/latest?shard_id={shard_id}')
        return Block(**data)

    # Smart Contract Methods
    async def deploy_contract(self, contract_type: str, params: Dict) -> SmartContract:
        """Deploy a new smart contract."""
        data = await self._request('POST', '/api/v1/contracts', json={
            'contract_type': contract_type,
            'params': params
        })
        return SmartContract(**data)

    async def call_contract(self, contract_address: str, method: str, 
                          params: Dict) -> Dict:
        """Call a smart contract method."""
        return await self._request('POST', f'/api/v1/contracts/{contract_address}/call', 
            json={'method': method, 'params': params})

    # Cross-Shard Operations
    async def initiate_cross_shard_transfer(self, from_shard: int, to_shard: int,
                                          transaction: Dict) -> CrossShardTransfer:
        """Initiate a cross-shard transfer."""
        data = await self._request('POST', '/api/v1/cross-shard/transfer', json={
            'from_shard': from_shard,
            'to_shard': to_shard,
            'transaction': transaction
        })
        return CrossShardTransfer(**data)

    # WebSocket Subscriptions
    async def subscribe_to_blocks(self, shard_id: int = 0):
        """Subscribe to new blocks in real-time."""
        ws_url = f"{self.node_url.replace('http', 'ws')}/ws/blocks?shard_id={shard_id}"
        async with websockets.connect(ws_url) as websocket:
            while True:
                try:
                    data = await websocket.recv()
                    block_data = json.loads(data)
                    yield Block(**block_data)
                except websockets.WebSocketException as e:
                    raise NetworkError(f"WebSocket error: {str(e)}")

    async def subscribe_to_transactions(self, shard_id: int = 0):
        """Subscribe to new transactions in real-time."""
        ws_url = f"{self.node_url.replace('http', 'ws')}/ws/transactions?shard_id={shard_id}"
        async with websockets.connect(ws_url) as websocket:
            while True:
                try:
                    data = await websocket.recv()
                    tx_data = json.loads(data)
                    yield Transaction(**tx_data)
                except websockets.WebSocketException as e:
                    raise NetworkError(f"WebSocket error: {str(e)}")

    # Validator Operations
    async def get_validator_set(self, shard_id: int = 0) -> List[Validator]:
        """Get the current validator set for a shard."""
        data = await self._request('GET', f'/api/v1/validators?shard_id={shard_id}')
        return [Validator(**v) for v in data['validators']]

    async def stake(self, amount: float, validator_address: str) -> Dict:
        """Stake tokens for validation."""
        return await self._request('POST', '/api/v1/stake', json={
            'amount': amount,
            'validator_address': validator_address
        })

    # Bridge Operations
    async def bridge_transfer(self, target_chain: str, amount: float, 
                            recipient: str) -> BridgeTransfer:
        """Initiate a cross-chain bridge transfer."""
        data = await self._request('POST', '/api/v1/bridge/transfer', json={
            'target_chain': target_chain,
            'amount': amount,
            'recipient': recipient
        })
        return BridgeTransfer(**data)