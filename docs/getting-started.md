# Getting Started with Vernachain

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BronzonTech-Cloud/vernachain.git
cd vernachain
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Start a Node
```bash
python -m src.cli start-node
```

### 2. Create a Wallet
```bash
python -m src.cli create-wallet
```

### 3. Become a Validator
```bash
python -m src.cli stake --amount 1000
```

## Basic Operations

### Send Transaction
```python
from src.blockchain.transaction import Transaction
from src.utils.crypto import generate_keypair

# Create and sign transaction
private_key, public_key = generate_keypair()
tx = Transaction(
    from_address=public_key,
    to_address="recipient_address",
    value=100,
    nonce=1
)
tx.sign(private_key)

# Submit transaction
response = node.submit_transaction(tx)
print(f"Transaction hash: {response['hash']}")
```

### Deploy Smart Contract
```python
# Deploy token contract
contract_code = """
class Contract:
    def __init__(self, name: str, symbol: str, total_supply: float):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.balances = {globals()['sender']: total_supply}
"""

contract_address = node.deploy_contract(
    code=contract_code,
    constructor_args=["MyToken", "MTK", 1000000]
)
print(f"Contract deployed at: {contract_address}")
```

### Cross-Shard Transaction
```python
# Create cross-shard transaction
tx = Transaction(
    from_address=public_key,
    to_address="recipient_address",
    value=100,
    nonce=1
)
tx.sign(private_key)

# Submit to source shard
source_shard = node.get_shard_for_address(public_key)
response = source_shard.submit_transaction(tx)
print(f"Cross-shard transaction initiated: {response['hash']}")
```

## Advanced Features

### Validator Operations
```python
# Check validator status
validator_info = node.get_validator_info(public_key)
print(f"Stake: {validator_info['stake']}")
print(f"Reputation: {validator_info['reputation_score']}")

# Claim rewards
rewards = node.claim_validator_rewards(public_key)
print(f"Claimed rewards: {rewards}")
```

### Smart Contract Interaction
```python
# Call contract method
result = node.call_contract(
    address=contract_address,
    method="transfer",
    args=["recipient_address", 100]
)
print(f"Transfer result: {result}")
```

### Monitor Events
```python
# Subscribe to new blocks
async def handle_block(block):
    print(f"New block: {block['index']}")
    print(f"Transactions: {len(block['transactions'])}")

node.subscribe_blocks(handle_block)

# Subscribe to transactions
async def handle_transaction(tx):
    print(f"New transaction: {tx['hash']}")
    print(f"Amount: {tx['amount']}")

node.subscribe_transactions(handle_transaction)
```

## Best Practices

### Security
- Always verify transaction signatures
- Use appropriate gas limits
- Keep private keys secure
- Monitor validator performance

### Performance
- Batch transactions when possible
- Use appropriate shard selection
- Implement proper error handling
- Cache frequently accessed data

### Development
- Test contracts thoroughly
- Monitor gas usage
- Handle cross-shard scenarios
- Implement proper logging

## Next Steps
- Explore the [API Reference](api-reference.md)
- Read the [Architecture Overview](architecture.md)
- Learn about [Smart Contracts](smart-contracts.md)
- Join the community

## Troubleshooting

Common issues and solutions:

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **Node Sync Issues**
   - Check network connectivity
   - Verify bootstrap nodes are accessible
   - Clear node data and resync

3. **Frontend Build Errors**
   - Clear npm cache
   - Update node modules
   - Check for conflicting dependencies

## Support

- GitHub Issues: [Report a bug](https://github.com/BronzonTech-Cloud/vernachain/issues)
