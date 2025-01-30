# JavaScript/TypeScript SDK Installation

## Prerequisites
- Node.js (v16+)
- npm or yarn package manager
- Basic knowledge of JavaScript/TypeScript

## Installation

### Using npm
```bash
npm install @vernachain/sdk
```

### Using yarn
```bash
yarn add @vernachain/sdk
```

## TypeScript Support
The SDK is written in TypeScript and includes type definitions out of the box. No additional packages are required.

## Basic Setup

### CommonJS
```javascript
const { VernachainClient } = require('@vernachain/sdk');

const client = new VernachainClient({
    nodeUrl: 'http://localhost:8545',
    apiKey: 'your-api-key'
});
```

### ES Modules
```javascript
import { VernachainClient } from '@vernachain/sdk';

const client = new VernachainClient({
    nodeUrl: 'http://localhost:8545',
    apiKey: 'your-api-key'
});
```

### TypeScript
```typescript
import { VernachainClient, TransactionRequest } from '@vernachain/sdk';

const client = new VernachainClient({
    nodeUrl: 'http://localhost:8545',
    apiKey: 'your-api-key'
});

const tx: TransactionRequest = {
    sender: '0xSender',
    recipient: '0xRecipient',
    amount: '1000000000000000000',
    shard_id: 0
};
```

## Configuration Options

### Client Configuration
```typescript
interface ClientConfig {
    nodeUrl: string;          // Required: URL of the Vernachain node
    apiKey?: string;          // Optional: API key for authentication
    timeout?: number;         // Optional: Request timeout in milliseconds
    retries?: number;         // Optional: Number of retry attempts
    logger?: Logger;          // Optional: Custom logger implementation
    network?: string;         // Optional: Network identifier
}
```

### Environment Variables
The SDK can be configured using environment variables:
```bash
VERNACHAIN_NODE_URL=http://localhost:8545
VERNACHAIN_API_KEY=your-api-key
VERNACHAIN_TIMEOUT=30000
VERNACHAIN_RETRIES=3
```

## Verification

### Connection Test
```javascript
// Test connection
try {
    const status = await client.getNodeStatus();
    console.log('Connected successfully:', status);
} catch (error) {
    console.error('Connection failed:', error);
}
```

### Version Check
```javascript
// Check SDK version
console.log('SDK Version:', client.version);

// Check node version compatibility
const nodeInfo = await client.getNodeInfo();
console.log('Node Version:', nodeInfo.version);
```

## Next Steps

After installation, you can:
1. Follow the [Basic Usage Guide](basic-usage.md)
2. Explore [Advanced Features](advanced-features.md)
3. Check the [API Reference](api-reference.md)

## Troubleshooting

### Common Installation Issues

1. **Node.js Version Mismatch**
```bash
# Check Node.js version
node --version

# Update Node.js if needed
nvm install 16
nvm use 16
```

2. **Package Conflicts**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

3. **TypeScript Errors**
```bash
# Check TypeScript version
npm list typescript

# Install specific version if needed
npm install typescript@4.8.4 --save-dev
```

### Getting Help
- Check [GitHub Issues](https://github.com/BronzonTech-Cloud/vernachain/issues)