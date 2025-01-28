---
layout: default
title: Vernachain Documentation
nav_order: 1
---

# Vernachain Documentation

Welcome to the Vernachain documentation. This guide will help you understand and use the Vernachain SDK effectively.

## Quick Start

```python
from vernachain import VernaChain

# Initialize the client
client = VernaChain(node_url="YOUR_NODE_URL")

# Create a new wallet
wallet = client.create_wallet()

# Get balance
balance = client.get_balance(wallet.address)
```

## Features

- Fast and efficient blockchain operations
- Built-in caching system
- Batch operation support
- WebSocket integration
- Comprehensive security features
- Smart contract deployment and interaction
- Command-line interface tools
- Advanced node operations

## Documentation Structure

### Core Documentation
1. [Getting Started](./getting-started.md)
   - Basic setup and installation
   - First steps with Vernachain
   - Basic operations

2. [Node Operation](./node-operation.md)
   - Node setup and configuration
   - Network participation
   - Validator operations

3. [CLI Tool Guide](./cli-tool.md)
   - Command-line interface usage
   - Available commands
   - Configuration options

### Development
4. [Smart Contracts](./smart-contracts.md)
   - Writing smart contracts
   - Deployment process
   - Contract interaction
   - Best practices

5. [API Reference](./api-reference.md)
   - Complete API documentation
   - Endpoints and methods
   - Request/response formats
   - Authentication

6. [Architecture](./architecture.md)
   - System design
   - Component interaction
   - Technical specifications
   - Security model

## Support and Community

- For technical support, please open an issue on our [GitHub repository](https://github.com/BronzonTech-Cloud/vernachain)


## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/BronzonTech-Cloud/vernachain/blob/main/CONTRIBUTING.md) for details on how to get started. 