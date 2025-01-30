# Basic Usage Guide

## Client Initialization

```typescript
import { VernachainClient } from '@vernachain/sdk';

const client = new VernachainClient({
    nodeUrl: 'http://localhost:8545',
    apiKey: 'your-api-key'
});
```

## Account Operations

### Creating an Account
```typescript
// Generate new account
const account = await client.createAccount();
console.log('Address:', account.address);
console.log('Private Key:', account.privateKey);

// Import existing account
const importedAccount = await client.importAccount(privateKey);
```

### Checking Balance
```typescript
const balance = await client.getBalance('0xYourAddress');
console.log('Balance:', balance);

// Check balance in specific shard
const shardBalance = await client.getBalance('0xYourAddress', { shard_id: 1 });
```

## Basic Transactions

### Sending Transactions
```typescript
// Simple transfer
const tx = await client.createTransaction({
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000', // 1 token
    shard_id: 0
});

// Wait for confirmation
const receipt = await client.waitForTransaction(tx.hash);
console.log('Transaction confirmed:', receipt);
```

### Transaction Status
```typescript
// Check transaction status
const status = await client.getTransactionStatus(tx.hash);
console.log('Status:', status);

// Get transaction details
const details = await client.getTransaction(tx.hash);
console.log('Details:', details);
```

## Smart Contract Interaction

### Loading a Contract
```typescript
const contractAbi = [...]; // Your contract ABI
const contractAddress = '0xContractAddress';

const contract = await client.loadContract(contractAddress, contractAbi);
```

### Reading Contract State
```typescript
// Call view function
const balance = await contract.methods.balanceOf('0xAddress').call();
console.log('Token Balance:', balance);

// Read multiple values
const [name, symbol, decimals] = await Promise.all([
    contract.methods.name().call(),
    contract.methods.symbol().call(),
    contract.methods.decimals().call()
]);
```

### Writing to Contract
```typescript
// Send transaction to contract
const result = await contract.methods.transfer('0xRecipient', '1000000000000000000').send({
    from: '0xSender',
    gas_limit: 100000
});

// Wait for confirmation
const receipt = await client.waitForTransaction(result.hash);
```

## Event Handling

### Subscribing to Events
```typescript
// Listen for new blocks
client.on('block', (block) => {
    console.log('New block:', block.number);
});

// Listen for specific transactions
client.on('transaction', (tx) => {
    if (tx.sender === myAddress) {
        console.log('My transaction:', tx);
    }
});
```

### Contract Events
```typescript
// Listen for contract events
contract.events.Transfer()
    .on('data', (event) => {
        console.log('Transfer:', {
            from: event.returnValues.from,
            to: event.returnValues.to,
            value: event.returnValues.value
        });
    })
    .on('error', console.error);
```

## Error Handling

### Basic Error Handling
```typescript
try {
    const result = await client.createTransaction({...});
} catch (error) {
    if (error.code === 'INSUFFICIENT_FUNDS') {
        console.error('Not enough funds');
    } else if (error.code === 'NETWORK_ERROR') {
        console.error('Network issue:', error.message);
    } else {
        console.error('Unknown error:', error);
    }
}
```

### Transaction Error Handling
```typescript
try {
    const tx = await contract.methods.transfer(recipient, amount).send({
        from: sender,
        gas_limit: 100000
    });
    
    const receipt = await client.waitForTransaction(tx.hash);
    if (receipt.status === 'failed') {
        console.error('Transaction failed:', receipt.error);
    }
} catch (error) {
    console.error('Transaction error:', error);
}
```

## Utility Functions

### Gas Estimation
```typescript
// Estimate transaction gas
const gasEstimate = await client.estimateGas({
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000'
});

// Estimate contract method gas
const methodGas = await contract.methods.transfer(recipient, amount)
    .estimateGas({ from: sender });
```

### Network Information
```typescript
// Get network status
const status = await client.getNodeStatus();
console.log('Node status:', status);

// Get current gas price
const gasPrice = await client.getGasPrice();
console.log('Current gas price:', gasPrice);
```

## Best Practices

### Connection Management
```typescript
// Check connection before operations
if (await client.isConnected()) {
    // Proceed with operations
} else {
    // Handle connection issue
}

// Cleanup
client.disconnect();
```

### Transaction Building
```typescript
// Build transaction with proper gas settings
const tx = await client.createTransaction({
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000',
    gas_price: await client.getGasPrice(),
    gas_limit: gasEstimate * 1.2 // Add 20% buffer
});
```

### Async Operations
```typescript
// Handle multiple operations
const [balance, transactions] = await Promise.all([
    client.getBalance(address),
    client.getTransactions(address)
]);

// Process results
console.log('Balance:', balance);
console.log('Transaction count:', transactions.length);
``` 