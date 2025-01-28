"""
Vernachain Python SDK.

This module provides a Python interface for interacting with the Vernachain blockchain.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
import httpx
import json
import asyncio
from .errors import (
    VernachainError, TransactionError, NetworkError,
    ValidationError, ContractError, BridgeError,
    AuthenticationError, RateLimitError
)
from .rate_limiter import RateLimiter
from .cache import CacheManager
from .websocket import WebsocketClient, WebsocketEvent

@dataclass
class Transaction:
    hash: str
    from_address: str
    to_address: str
    value: float
    timestamp: datetime
    status: str
    block_number: Optional[int] = None
    gas_used: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        try:
            return cls(
                hash=data['hash'],
                from_address=data['from_address'],
                to_address=data['to_address'],
                value=data['value'],
                timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                status=data['status'],
                block_number=data.get('block_number'),
                gas_used=data.get('gas_used')
            )
        except KeyError as e:
            raise ValidationError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValidationError(f"Invalid data format: {e}")

@dataclass
class Block:
    number: int
    hash: str
    timestamp: datetime
    transactions: List[str]
    validator: str
    size: int

    @classmethod
    def from_dict(cls, data: Dict) -> 'Block':
        return cls(
            number=data['number'],
            hash=data['hash'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            transactions=data['transactions'],
            validator=data['validator'],
            size=data['size']
        )

@dataclass
class Contract:
    address: str
    creator: str
    creation_tx: str
    bytecode: str
    abi: Dict

    @classmethod
    def from_dict(cls, data: Dict) -> 'Contract':
        return cls(
            address=data['address'],
            creator=data['creator'],
            creation_tx=data['creation_tx'],
            bytecode=data['bytecode'],
            abi=data['abi']
        )

class VernachainSDK:
    """Main SDK class for interacting with Vernachain."""
    
    def __init__(self, api_url: str, api_key: str, enable_cache: bool = True,
                 enable_websocket: bool = True):
        """
        Initialize the SDK with API URL and key.
        
        Args:
            api_url: Base URL for API
            api_key: API key for authentication
            enable_cache: Whether to enable caching
            enable_websocket: Whether to enable websocket connection
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        self.rate_limiter = RateLimiter()
        self.cache_manager = CacheManager() if enable_cache else None
        self.ws_client = None
        if enable_websocket:
            ws_url = self.api_url.replace('http', 'ws') + '/ws'
            self.ws_client = WebsocketClient(ws_url)
        try:
            self.client = httpx.Client(headers=self.headers)
        except Exception as e:
            raise NetworkError(f"Failed to initialize HTTP client: {e}")

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request with error handling."""
        url = f"{self.api_url}{endpoint}"
        try:
            response = await self.client.request(method, url, json=data)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code >= 400:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Unknown error')
                if response.status_code >= 500:
                    raise NetworkError(f"Server error: {error_msg}")
                else:
                    raise VernachainError(f"API error: {error_msg}")
                    
            return response.json()
            
        except httpx.TimeoutException:
            raise NetworkError("Request timed out")
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}")
        except json.JSONDecodeError:
            raise NetworkError("Invalid JSON response")

    async def get_block(self, block_id: int) -> Dict:
        """Get block details by ID."""
        try:
            data = await self._request('GET', f"/api/v1/block/{block_id}")
            return data
        except VernachainError:
            raise
        except Exception as e:
            raise NetworkError(f"Failed to get block: {e}")

    async def get_transaction(self, tx_hash: str) -> Transaction:
        """Get transaction details by hash."""
        try:
            data = await self._request('GET', f"/api/v1/transaction/{tx_hash}")
            return Transaction.from_dict(data)
        except ValidationError:
            raise
        except VernachainError:
            raise
        except Exception as e:
            raise TransactionError(f"Failed to get transaction: {e}")

    def get_balance(self, address: str) -> float:
        """Get address balance."""
        response = self.client.get(
            f"{self.api_url}/api/v1/address/{address}"
        )
        response.raise_for_status()
        return float(response.json()['balance'])

    async def send_transaction(self, to_address: str, value: float, 
                             private_key: str, gas_limit: Optional[int] = None) -> str:
        """Send a transaction."""
        try:
            data = {
                'to_address': to_address,
                'value': value,
                'private_key': private_key,
                'gas_limit': gas_limit
            }
            response = await self._request('POST', '/api/v1/transaction', data)
            return response['transaction_hash']
        except VernachainError:
            raise
        except Exception as e:
            raise TransactionError(f"Failed to send transaction: {e}")

    async def deploy_contract(self, bytecode: str, abi: Dict,
                            private_key: str, gas_limit: Optional[int] = None) -> str:
        """Deploy a smart contract."""
        try:
            data = {
                'bytecode': bytecode,
                'abi': abi,
                'private_key': private_key,
                'gas_limit': gas_limit
            }
            response = await self._request('POST', '/api/v1/contract/deploy', data)
            return response['contract_address']
        except VernachainError:
            raise
        except Exception as e:
            raise ContractError(f"Failed to deploy contract: {e}")

    def call_contract(
        self,
        contract_address: str,
        function_name: str,
        args: List,
        abi: Dict
    ) -> Any:
        """Call a contract function."""
        payload = {
            'contract_address': contract_address,
            'function_name': function_name,
            'args': args,
            'abi': abi
        }
        response = self.client.post(
            f"{self.api_url}/api/v1/contract/{contract_address}/call",
            json=payload
        )
        response.raise_for_status()
        return response.json()['result']

    async def bridge_transfer(self, from_chain: str, to_chain: str,
                            token: str, amount: float, to_address: str,
                            private_key: str) -> str:
        """Initiate a cross-chain transfer."""
        try:
            data = {
                'from_chain': from_chain,
                'to_chain': to_chain,
                'token': token,
                'amount': amount,
                'to_address': to_address,
                'private_key': private_key
            }
            response = await self._request('POST', '/api/v1/bridge/transfer', data)
            return response['bridge_tx_hash']
        except VernachainError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to initiate bridge transfer: {e}")

    def get_bridge_transaction(self, tx_hash: str) -> Dict:
        """Get bridge transaction status."""
        response = self.client.get(
            f"{self.api_url}/api/v1/bridge/transaction/{tx_hash}"
        )
        response.raise_for_status()
        return response.json()

    def get_network_stats(self) -> Dict:
        """Get network statistics."""
        response = self.client.get(
            f"{self.api_url}/api/v1/stats"
        )
        response.raise_for_status()
        return response.json()

    def get_validators(self) -> List[Dict]:
        """Get list of validators and their stats."""
        response = self.client.get(
            f"{self.api_url}/api/v1/validators"
        )
        response.raise_for_status()
        return response.json()

    async def subscribe_to_events(self, event_type: str, handler: Callable[[WebsocketEvent], None]) -> None:
        """
        Subscribe to blockchain events.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async callback function for handling events
        """
        if not self.ws_client:
            raise NetworkError("Websocket support not enabled")
        await self.ws_client.subscribe(event_type, handler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close() 