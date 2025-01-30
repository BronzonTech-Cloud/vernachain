import pytest
import aiohttp
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

from vernachain_sdk import VernachainClient
from vernachain_sdk.models import (
    Block,
    Transaction,
    TransactionRequest,
    ContractDeployRequest,
)
from vernachain_sdk.exceptions import (
    AuthenticationError,
    HTTPError,
    RateLimitError,
)

@pytest.fixture
def client():
    return VernachainClient("http://test-node", api_key="test-key")

@pytest.fixture
def mock_response():
    def _create_response(status, data):
        response = AsyncMock()
        response.status = status
        response.ok = 200 <= status < 300
        response.json = AsyncMock(return_value=data)
        response.text = AsyncMock(return_value=json.dumps(data))
        return response
    return _create_response

@pytest.mark.asyncio
async def test_create_transaction(client, mock_response):
    tx_data = {
        "hash": "0x123...",
        "sender": "0x456...",
        "recipient": "0x789...",
        "amount": 1.0,
        "timestamp": datetime.utcnow().isoformat(),
        "shard_id": 0,
        "status": "pending"
    }
    
    with patch.object(client, "_request", AsyncMock(return_value=Transaction(**tx_data))):
        request = TransactionRequest(
            sender="0x456...",
            recipient="0x789...",
            amount=1.0,
            shard_id=0
        )
        tx = await client.create_transaction(request)
        
        assert isinstance(tx, Transaction)
        assert tx.hash == "0x123..."
        assert tx.amount == 1.0

@pytest.mark.asyncio
async def test_get_latest_block(client, mock_response):
    block_data = {
        "number": 1000,
        "hash": "0xabc...",
        "previous_hash": "0xdef...",
        "timestamp": datetime.utcnow().isoformat(),
        "transactions": [],
        "validator": "0x111...",
        "shard_id": 0,
        "merkle_root": "0x222...",
        "state_root": "0x333..."
    }
    
    with patch.object(client, "_request", AsyncMock(return_value=Block(**block_data))):
        block = await client.get_latest_block(0)
        
        assert isinstance(block, Block)
        assert block.number == 1000
        assert block.shard_id == 0

@pytest.mark.asyncio
async def test_authentication_error(client, mock_response):
    with patch.object(client, "_request", AsyncMock(side_effect=AuthenticationError("Invalid API key"))):
        with pytest.raises(AuthenticationError):
            await client.get_latest_block(0)

@pytest.mark.asyncio
async def test_rate_limit_error(client, mock_response):
    with patch.object(client, "_request", AsyncMock(side_effect=RateLimitError("Rate limit exceeded"))):
        with pytest.raises(RateLimitError):
            await client.get_latest_block(0)

@pytest.mark.asyncio
async def test_http_error(client, mock_response):
    with patch.object(client, "_request", AsyncMock(side_effect=HTTPError(500, "Internal server error"))):
        with pytest.raises(HTTPError) as exc_info:
            await client.get_latest_block(0)
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_deploy_contract(client, mock_response):
    contract_data = {
        "address": "0xcontract...",
        "contract_type": "ERC20",
        "creator": "0x456...",
        "creation_timestamp": datetime.utcnow().isoformat(),
        "shard_id": 0,
        "abi": {},
        "bytecode": "0x..."
    }
    
    with patch.object(client, "_request", AsyncMock(return_value=contract_data)):
        request = ContractDeployRequest(
            contract_type="ERC20",
            params={"name": "Test", "symbol": "TST"},
            shard_id=0
        )
        contract = await client.deploy_contract(request)
        
        assert contract["address"] == "0xcontract..."
        assert contract["contract_type"] == "ERC20"

@pytest.mark.asyncio
async def test_context_manager(client):
    async with client as c:
        assert c.session is not None
    assert client.session is None 