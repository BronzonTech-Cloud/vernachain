 # Vernachain Python SDK v2

A comprehensive Python SDK for interacting with the Vernachain blockchain platform.

## Features

- Async/await support for all operations
- Type-safe transaction and block handling
- Smart contract deployment and interaction
- Cross-shard transaction support
- Real-time updates via WebSocket
- Validator operations
- Bridge transfer functionality

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
import asyncio
from vernachain_sdk import VernachainClient

async def main():
    # Initialize client
    client = VernachainClient("http://node-url", api_key="your-api-key")
    
    # Create transaction
    tx = await client.create_transaction(
        sender="0x...",
        recipient="0x...",
        amount=1.0,
        shard_id=0
    )
    
    # Get block
    block = await client.get_latest_block(shard_id=0)
    
    # Deploy smart contract
    contract = await client.deploy_contract(
        contract_type="ERC20",
        params={"name": "MyToken", "symbol": "MTK"}
    )
    
    # Subscribe to new blocks
    async for block in client.subscribe_to_blocks(shard_id=0):
        print(f"New block: {block.number}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### Transaction Methods
- `create_transaction(sender, recipient, amount, shard_id=0)`
- `get_transaction(tx_hash)`

### Block Methods
- `get_block(block_number, shard_id=0)`
- `get_latest_block(shard_id=0)`

### Smart Contract Methods
- `deploy_contract(contract_type, params)`
- `call_contract(contract_address, method, params)`

### Cross-Shard Operations
- `initiate_cross_shard_transfer(from_shard, to_shard, transaction)`

### WebSocket Subscriptions
- `subscribe_to_blocks(shard_id=0)`
- `subscribe_to_transactions(shard_id=0)`

### Validator Operations
- `get_validator_set(shard_id=0)`
- `stake(amount, validator_address)`

### Bridge Operations
- `bridge_transfer(target_chain, amount, recipient)`

## Error Handling

The SDK uses custom exceptions for different error cases:
- `VernachainError`: Base exception class
- `ValidationError`: Input validation errors
- `NetworkError`: Network-related errors
- `AuthenticationError`: API key/auth issues

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.