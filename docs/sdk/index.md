# Vernachain SDK Documentation

## Overview
The Vernachain SDK provides a simple and intuitive way to interact with the Vernachain network. Currently, we support JavaScript/TypeScript and PHP, with more languages planned for the future.

## Available SDKs

### JavaScript/TypeScript SDK
- [Installation & Setup](javascript/installation.md)
- [Basic Usage](javascript/basic-usage.md)
- [Advanced Features](javascript/advanced-features.md)
- [API Reference](javascript/api-reference.md)

### PHP SDK
- [Installation & Setup](php/installation.md)
- [Basic Usage](php/basic-usage.md)
- [Advanced Features](php/advanced-features.md)
- [API Reference](php/api-reference.md)

## Quick Start

### JavaScript/TypeScript
```javascript
import { VernachainClient } from '@vernachain/sdk';

// Initialize client
const client = new VernachainClient({
    nodeUrl: 'http://localhost:8545',
    apiKey: 'your-api-key'
});

// Send transaction
const tx = await client.createTransaction({
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000',
    shard_id: 0
});

// Smart contract interaction
const contract = await client.loadContract(contractAddress, contractAbi);
const result = await contract.methods.transfer(recipient, amount).send({
    from: sender,
    gas_limit: 100000
});
```

### PHP
```php
use Vernachain\SDK\VernachainClient;

// Initialize client
$client = new VernachainClient([
    'node_url' => 'http://localhost:8545',
    'api_key' => 'your-api-key'
]);

// Send transaction
$tx = $client->createTransaction([
    'sender' => '0xSender',
    'recipient' => '0xRecipient',
    'amount' => '1000000000000000000',
    'shard_id' => 0
]);

// Smart contract interaction
$contract = $client->loadContract($contractAddress, $contractAbi);
$result = $contract->methods->transfer($recipient, $amount)->send([
    'from' => $sender,
    'gas_limit' => 100000
]);
```

## Common Features

### Transaction Management
- Creating and sending transactions
- Transaction status monitoring
- Gas estimation and management
- Transaction receipt retrieval

### Smart Contract Interaction
- Contract deployment
- Method calls (read/write)
- Event listening
- Gas optimization

### Cross-Shard Operations
- Cross-shard transfers
- State verification
- Message handling
- Error management

### Account Management
- Account creation
- Balance checking
- Key management
- Signature verification

## Best Practices

### Error Handling
```javascript
try {
    const result = await client.createTransaction({...});
} catch (error) {
    if (error.code === 'INSUFFICIENT_FUNDS') {
        // Handle insufficient funds
    } else if (error.code === 'NETWORK_ERROR') {
        // Handle network issues
    }
}
```

### Gas Management
```javascript
// Estimate gas before sending transaction
const gasEstimate = await client.estimateGas({
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000'
});

// Add buffer to estimate
const gasLimit = Math.ceil(gasEstimate * 1.2);
```

### Batch Operations
```javascript
// Batch multiple operations
const batch = await client.createBatch([
    {
        method: 'createTransaction',
        params: {...}
    },
    {
        method: 'deployContract',
        params: {...}
    }
]);
const results = await batch.execute();
```

## Common Patterns

### Event Listening
```javascript
// Listen for specific events
client.on('block', (block) => {
    console.log('New block:', block.number);
});

// Contract events
contract.events.Transfer()
    .on('data', (event) => {
        console.log('Transfer:', event.returnValues);
    })
    .on('error', console.error);
```

### State Management
```javascript
// Get and verify state
const state = await client.getState(address);
const proof = await client.getStateProof(address);
const isValid = await client.verifyStateProof(proof);
```

## Troubleshooting

### Common Issues
1. Connection Problems
   - Check network connectivity
   - Verify node URL
   - Confirm API key

2. Transaction Failures
   - Insufficient funds
   - Gas price too low
   - Nonce issues

3. Contract Interactions
   - ABI mismatches
   - Gas estimation failures
   - State inconsistencies

### Debug Tools
```javascript
// Enable debug logging
client.setLogLevel('debug');

// Get detailed error information
try {
    await operation();
} catch (error) {
    console.log('Error details:', error.details);
    console.log('Stack trace:', error.stack);
}
```

## Support Resources
- [GitHub Issues](https://github.com/BronzonTech-Cloud/vernachain/issues)

