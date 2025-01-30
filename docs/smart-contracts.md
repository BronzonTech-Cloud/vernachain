# Smart Contracts Guide

## Overview

Vernachain supports Python-based smart contracts with the following features:
- Gas metering and optimization
- State persistence
- Event emission
- Cross-contract calls
- Standard token interfaces

## Contract Types

### Token Contract (ERC20-like)
```python
class Contract:
    def __init__(self, name: str, symbol: str, total_supply: float):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.balances = {globals()['sender']: total_supply}
        self.allowances = {}
        
    def transfer(self, to: str, amount: float) -> bool:
        sender = globals()['sender']
        if self.balances.get(sender, 0) < amount:
            return False
        self.balances[sender] = self.balances.get(sender, 0) - amount
        self.balances[to] = self.balances.get(to, 0) + amount
        return True
```

### NFT Contract (ERC721-like)
```python
class Contract:
    def __init__(self, name: str, symbol: str, base_uri: str):
        self.name = name
        self.symbol = symbol
        self.base_uri = base_uri
        self.owner = globals()['sender']
        self.tokens = {}  # token_id -> owner
        self.token_uris = {}  # token_id -> uri
        self.balances = {}  # owner -> token count
        self.approved = {}  # token_id -> approved address
        
    def mint(self, to: str, token_id: int, uri: str) -> bool:
        assert globals()['sender'] == self.owner, "Not owner"
        assert token_id not in self.tokens, "Token exists"
        
        self.tokens[token_id] = to
        self.token_uris[token_id] = uri
        self.balances[to] = self.balances.get(to, 0) + 1
        return True
```

### Multi-Token Contract (ERC1155-like)
```python
class Contract:
    def __init__(self, uri: str):
        self.uri = uri
        self.owner = globals()['sender']
        self.balances = {}  # token_id -> owner -> amount
        self.operators = {}  # owner -> operator -> approved
        
    def mint(self, to: str, token_id: int, amount: int) -> bool:
        assert globals()['sender'] == self.owner, "Not owner"
        
        if token_id not in self.balances:
            self.balances[token_id] = {}
        self.balances[token_id][to] = self.balances[token_id].get(to, 0) + amount
        return True
```

## Gas System

### Gas Costs
```python
COSTS = {
    'LOAD': 1,    # Load from storage
    'STORE': 5,   # Store to storage
    'CALL': 10,   # Contract call
    'MATH': 2,    # Mathematical operation
    'TRANSFER': 20 # Token transfer
}
```

### Gas Usage Example
```python
def transfer(self, to: str, amount: float) -> bool:
    globals()['gas_counter'].charge('LOAD', 2)  # Load balances
    sender = globals()['sender']
    if self.balances.get(sender, 0) < amount:
        return False
        
    globals()['gas_counter'].charge('STORE', 2)  # Update balances
    self.balances[sender] -= amount
    self.balances[to] = self.balances.get(to, 0) + amount
    return True
```

## Contract Deployment

### Deploy Token Contract
```python
# Deploy contract
contract_address = node.deploy_contract(
    code=token_contract_code,
    constructor_args=["MyToken", "MTK", 1000000]
)

# Interact with contract
node.call_contract(
    address=contract_address,
    method="transfer",
    args=["recipient_address", 100]
)
```

### Deploy NFT Contract
```python
# Deploy contract
contract_address = node.deploy_contract(
    code=nft_contract_code,
    constructor_args=["MyNFT", "NFT", "https://api.example.com/token/"]
)

# Mint NFT
node.call_contract(
    address=contract_address,
    method="mint",
    args=["owner_address", 1, "token_1.json"]
)
```

## Best Practices

### Security
- Validate all inputs
- Use proper access control
- Handle edge cases
- Check arithmetic overflow
- Verify state changes

### Gas Optimization
- Minimize storage operations
- Batch operations when possible
- Use efficient data structures
- Cache frequently accessed values
- Optimize loops

### Development
- Test thoroughly
- Document code
- Use type hints
- Handle errors gracefully
- Emit events for important changes

## Contract Templates

### Vesting Contract
```python
class Contract:
    def __init__(self, token_address: str, beneficiary: str, 
                 start_time: int, duration: int, amount: float):
        self.token = token_address
        self.beneficiary = beneficiary
        self.start_time = start_time
        self.duration = duration
        self.amount = amount
        self.claimed = 0.0
```

### Staking Contract
```python
class Contract:
    def __init__(self, reward_rate: float):
        self.owner = globals()['sender']
        self.reward_rate = reward_rate
        self.stakes = {}  # address -> stake info
        self.total_staked = 0.0
```

### Governance Contract
```python
class Contract:
    def __init__(self, token_address: str, quorum: float):
        self.token = token_address
        self.quorum = quorum
        self.proposals = {}
        self.votes = {}
```

## Testing

### Unit Tests
```python
def test_token_transfer():
    # Deploy contract
    contract = deploy_test_contract(
        "TokenContract",
        ["TestToken", "TST", 1000]
    )
    
    # Test transfer
    assert contract.transfer("recipient", 100) == True
    assert contract.balances["recipient"] == 100
```

### Integration Tests
```python
def test_cross_contract_interaction():
    # Deploy contracts
    token = deploy_test_contract("TokenContract", ["Token", "TKN", 1000])
    vesting = deploy_test_contract(
        "VestingContract",
        [token.address, "beneficiary", time.time(), 86400, 100]
    )
    
    # Test interaction
    token.approve(vesting.address, 100)
    vesting.release()
```