 # Vernachain JavaScript/TypeScript SDK v2

A comprehensive TypeScript/JavaScript SDK for interacting with the Vernachain blockchain platform.

## Features

- Full TypeScript support with strong typing
- Runtime type validation using Zod
- Promise-based API with async/await
- Event-driven WebSocket subscriptions
- Comprehensive error handling
- Cross-shard transaction support
- Smart contract interactions
- Bridge operations

## Installation

```bash
npm install @vernachain/sdk
# or
yarn add @vernachain/sdk
```

## Quick Start

```typescript
import { VernachainClient } from '@vernachain/sdk';

// Initialize client
const client = new VernachainClient('http://node-url', 'your-api-key');

// Create transaction
const tx = await client.createTransaction({
  sender: '0x...',
  recipient: '0x...',
  amount: 1.0,
  shard_id: 0
});

// Get block
const block = await client.getLatestBlock(0);

// Deploy smart contract
const contract = await client.deployContract({
  contract_type: 'ERC20',
  params: {
    name: 'MyToken',
    symbol: 'MTK'
  }
});

// Subscribe to new blocks
client.subscribeToBlocks(0);
client.on('block', (block) => {
  console.log(`New block: ${block.number}`);
});

// Handle errors
client.on('error', (error) => {
  console.error('Error:', error.message);
});
```

## API Reference

### Transaction Methods
- `createTransaction(request: TransactionRequest): Promise<Transaction>`
- `getTransaction(txHash: string): Promise<Transaction>`

### Block Methods
- `getBlock(blockNumber: number, shardId?: number): Promise<Block>`
- `getLatestBlock(shardId?: number): Promise<Block>`

### Smart Contract Methods
- `deployContract(request: ContractDeployRequest): Promise<SmartContract>`
- `callContract(address: string, method: string, params: Record<string, unknown>): Promise<unknown>`

### Cross-Shard Operations
- `initiateCrossShardTransfer(request: CrossShardTransferRequest): Promise<CrossShardTransfer>`

### WebSocket Subscriptions
- `subscribeToBlocks(shardId?: number): void`
- `subscribeToTransactions(shardId?: number): void`

### Validator Operations
- `getValidatorSet(shardId?: number): Promise<Validator[]>`
- `stake(amount: number, validatorAddress: string): Promise<unknown>`

### Bridge Operations
- `bridgeTransfer(request: BridgeTransferRequest): Promise<BridgeTransfer>`

## Error Handling

The SDK provides several error types for different scenarios:
```typescript
import { 
  VernachainError,
  ValidationError,
  NetworkError,
  AuthenticationError
} from '@vernachain/sdk';

try {
  await client.createTransaction(/* ... */);
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation error
  } else if (error instanceof NetworkError) {
    // Handle network error
  } else if (error instanceof AuthenticationError) {
    // Handle authentication error
  }
}
```

## WebSocket Events

The client extends EventEmitter and emits the following events:
- `'block'`: Emitted when a new block is received
- `'transaction'`: Emitted when a new transaction is received
- `'error'`: Emitted when an error occurs in WebSocket connections

## Type Safety

All types are fully documented and validated at runtime:
```typescript
import type { 
  Transaction,
  Block,
  SmartContract,
  Validator,
  CrossShardTransfer,
  BridgeTransfer
} from '@vernachain/sdk';
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.