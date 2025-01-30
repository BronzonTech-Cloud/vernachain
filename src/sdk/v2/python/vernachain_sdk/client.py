import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar
import aiohttp
import websockets
from datetime import datetime

from .exceptions import (
    AuthenticationError,
    HTTPError,
    NetworkError,
    RateLimitError,
    UnexpectedResponseError,
    WebSocketClosedError,
)
from .models import (
    Block,
    BridgeTransfer,
    BridgeTransferRequest,
    ContractDeployRequest,
    CrossShardTransfer,
    CrossShardTransferRequest,
    SmartContract,
    Transaction,
    TransactionRequest,
    Validator,
)

T = TypeVar("T")

class VernachainClient:
    """Client for interacting with the Vernachain blockchain platform."""

    def __init__(
        self,
        node_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize the Vernachain client.

        Args:
            node_url: Base URL of the Vernachain node
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = node_url.rstrip("/")
        self.ws_url = node_url.replace("http", "ws").rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Set up async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context manager."""
        await self.close()

    async def connect(self):
        """Create HTTP session."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )

    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Any:
        """Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            model: Optional Pydantic model to parse response
            **kwargs: Additional arguments for request

        Returns:
            Parsed response data

        Raises:
            HTTPError: If request fails
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            NetworkError: If network error occurs
        """
        if not self.session:
            await self.connect()

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif not response.ok:
                    raise HTTPError(
                        response.status,
                        await response.text(),
                        {"url": url, "method": method},
                    )

                data = await response.json()
                return model.parse_obj(data) if model else data

        except aiohttp.ClientError as e:
            raise NetworkError(f"Request failed: {str(e)}")

    # Transaction Methods
    async def create_transaction(self, request: TransactionRequest) -> Transaction:
        """Create a new transaction."""
        return await self._request(
            "POST",
            "/api/v1/transactions",
            model=Transaction,
            json=request.dict(exclude_none=True),
        )

    async def get_transaction(self, tx_hash: str) -> Transaction:
        """Get transaction by hash."""
        return await self._request(
            "GET",
            f"/api/v1/transactions/{tx_hash}",
            model=Transaction,
        )

    # Block Methods
    async def get_block(self, block_number: int, shard_id: int) -> Block:
        """Get block by number and shard ID."""
        return await self._request(
            "GET",
            f"/api/v1/blocks/{block_number}",
            model=Block,
            params={"shard_id": shard_id},
        )

    async def get_latest_block(self, shard_id: int) -> Block:
        """Get latest block for shard."""
        return await self._request(
            "GET",
            "/api/v1/blocks/latest",
            model=Block,
            params={"shard_id": shard_id},
        )

    # Smart Contract Methods
    async def deploy_contract(self, request: ContractDeployRequest) -> SmartContract:
        """Deploy a new smart contract."""
        return await self._request(
            "POST",
            "/api/v1/contracts",
            model=SmartContract,
            json=request.dict(exclude_none=True),
        )

    async def call_contract(
        self,
        contract_address: str,
        method: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a smart contract method."""
        return await self._request(
            "POST",
            f"/api/v1/contracts/{contract_address}/call",
            json={"method": method, "params": params},
        )

    # Cross-Shard Operations
    async def initiate_cross_shard_transfer(
        self,
        request: CrossShardTransferRequest,
    ) -> CrossShardTransfer:
        """Initiate a cross-shard transfer."""
        return await self._request(
            "POST",
            "/api/v1/cross-shard/transfer",
            model=CrossShardTransfer,
            json=request.dict(exclude_none=True),
        )

    # WebSocket Subscriptions
    async def subscribe_blocks(self, shard_id: int) -> asyncio.Queue[Block]:
        """Subscribe to new blocks on a shard.

        Returns:
            Queue that receives new blocks
        """
        queue: asyncio.Queue[Block] = asyncio.Queue()
        ws_url = f"{self.ws_url}/ws/blocks?shard_id={shard_id}"

        async def _handler():
            while True:
                try:
                    async with websockets.connect(ws_url) as websocket:
                        if self.api_key:
                            await websocket.send(
                                {"type": "auth", "token": self.api_key}
                            )

                        async for message in websocket:
                            try:
                                block = Block.parse_raw(message)
                                await queue.put(block)
                            except Exception as e:
                                # Log error but continue processing
                                print(f"Error parsing block: {e}")

                except websockets.WebSocketException as e:
                    raise WebSocketClosedError(f"WebSocket connection failed: {e}")
                
                # Wait before reconnecting
                await asyncio.sleep(1)

        # Start handler task
        asyncio.create_task(_handler())
        return queue

    # Validator Operations
    async def get_validator_set(self, shard_id: int) -> List[Validator]:
        """Get validator set for shard."""
        return await self._request(
            "GET",
            "/api/v1/validators",
            model=List[Validator],
            params={"shard_id": shard_id},
        )

    async def stake(self, amount: float, validator_address: str) -> Dict[str, Any]:
        """Stake tokens on a validator."""
        return await self._request(
            "POST",
            "/api/v1/stake",
            json={
                "amount": amount,
                "validator_address": validator_address,
            },
        )

    # Bridge Operations
    async def bridge_transfer(self, request: BridgeTransferRequest) -> BridgeTransfer:
        """Initiate a bridge transfer."""
        return await self._request(
            "POST",
            "/api/v1/bridge/transfer",
            model=BridgeTransfer,
            json=request.dict(exclude_none=True),
        ) 