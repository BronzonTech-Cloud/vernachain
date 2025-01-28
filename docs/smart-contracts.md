# Smart Contracts in Vernachain

This guide covers writing, deploying, and interacting with smart contracts on Vernachain.

## Overview

Vernachain smart contracts are written in Python and executed in a secure virtual machine. The system provides:

- Deterministic execution
- Gas metering
- State persistence
- Event emission
- Cross-contract calls

## Writing Smart Contracts

### Basic Contract Structure

```python
class MyContract:
    def __init__(self):
        """Constructor - called when contract is deployed."""
        self.owner = globals()['sender']
        self.value = 0
        
    def set_value(self, new_value: int):
        """Update the stored value."""
        # Access execution context
        sender = globals()['sender']
        gas_counter = globals()['gas_counter']
        
        # Charge gas for storage operation
        gas_counter.charge(10)
        
        # Only owner can update
        assert sender == self.owner, "Not authorized"
        self.value = new_value
        
    def get_value(self) -> int:
        """Read the stored value."""
        # Read operations are free
        return self.value
```

### Contract Storage

- Instance variables are automatically persisted
- Support for basic Python types and structures
- Complex objects must be serializable
- Storage operations cost gas

### Access Control

- `globals()['sender']`: Transaction sender address
- `globals()['value']`: Amount of VERNA sent with call
- `globals()['gas_counter']`: Gas tracking object
- `globals()['block']`: Current block information

### Gas System

```python
# Gas costs for operations
gas_counter.charge(10)  # Basic operation
gas_counter.charge_storage(32)  # Storage operation
gas_counter.charge_compute(100)  # Heavy computation
```

## Token Contract Example

Here's a complete ERC20-like token contract:

```python
class Token:
    def __init__(self, name: str, symbol: str, total_supply: int):
        """Initialize the token contract."""
        self.name = name
        self.symbol = symbol
        self.decimals = 18
        self.total_supply = total_supply
        
        # Storage
        self.balances = {globals()['sender']: total_supply}
        self.allowances = {}
        
        # Events
        self.Transfer = Event('Transfer')
        self.Approval = Event('Approval')
        
    def balance_of(self, account: str) -> int:
        """Get the token balance of an account."""
        return self.balances.get(account, 0)
        
    def transfer(self, to: str, amount: int) -> bool:
        """Transfer tokens to another address."""
        sender = globals()['sender']
        gas_counter = globals()['gas_counter']
        
        # Charge gas
        gas_counter.charge(100)
        
        # Check balance
        assert self.balances.get(sender, 0) >= amount, "Insufficient balance"
        
        # Update balances
        self.balances[sender] = self.balances.get(sender, 0) - amount
        self.balances[to] = self.balances.get(to, 0) + amount
        
        # Emit event
        self.Transfer.emit(sender, to, amount)
        return True
        
    def approve(self, spender: str, amount: int) -> bool:
        """Approve spender to spend tokens."""
        sender = globals()['sender']
        gas_counter = globals()['gas_counter']
        
        gas_counter.charge(50)
        
        if sender not in self.allowances:
            self.allowances[sender] = {}
            
        self.allowances[sender][spender] = amount
        self.Approval.emit(sender, spender, amount)
        return True
        
    def transfer_from(self, from_addr: str, to: str, amount: int) -> bool:
        """Transfer tokens on behalf of another address."""
        sender = globals()['sender']
        gas_counter = globals()['gas_counter']
        
        gas_counter.charge(150)
        
        # Check allowance
        allowed = self.allowances.get(from_addr, {}).get(sender, 0)
        assert allowed >= amount, "Insufficient allowance"
        
        # Check balance
        assert self.balances.get(from_addr, 0) >= amount, "Insufficient balance"
        
        # Update balances
        self.balances[from_addr] -= amount
        self.balances[to] = self.balances.get(to, 0) + amount
        
        # Update allowance
        self.allowances[from_addr][sender] -= amount
        
        self.Transfer.emit(from_addr, to, amount)
        return True
```

## Deployment and Interaction

### Deploying Contracts

Using CLI:
```bash
python -m src.cli deploy 0xsender...addr token.py \
    --args '{"name": "MyToken", "symbol": "MTK", "total_supply": 1000000}'
```

Using SDK:
```python
from src.sdk.vernachain import VernaChainSDK

sdk = VernaChainSDK()
await sdk.connect()

# Deploy contract
contract_addr = await sdk.deploy_contract(
    from_address="0xsender...addr",
    code=open("token.py").read(),
    constructor_args=["MyToken", "MTK", 1000000]
)
```

### Calling Contract Functions

Using CLI:
```bash
# Transfer tokens
python -m src.cli call 0xsender...addr 0xcontract...addr transfer \
    --args '{"to": "0xrecipient...addr", "amount": 100}'

# Check balance
python -m src.cli call 0xsender...addr 0xcontract...addr balance_of \
    --args '{"account": "0xrecipient...addr"}'
```

Using SDK:
```python
# Transfer tokens
result = await sdk.call_contract(
    contract_address="0xcontract...addr",
    from_address="0xsender...addr",
    function_name="transfer",
    args=["0xrecipient...addr", 100]
)

# Check balance
balance = await sdk.call_contract(
    contract_address="0xcontract...addr",
    from_address="0xsender...addr",
    function_name="balance_of",
    args=["0xrecipient...addr"]
)
```

## Best Practices

1. **Gas Optimization**
   - Minimize storage operations
   - Batch operations when possible
   - Use appropriate data structures

2. **Security**
   - Always validate inputs
   - Check permissions
   - Use assert for invariants
   - Handle edge cases

3. **Testing**
   - Write unit tests
   - Test with different inputs
   - Verify gas consumption
   - Test permission checks

4. **Events**
   - Emit events for state changes
   - Include relevant information
   - Use for off-chain tracking 