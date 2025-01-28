# Vernachain Documentation

Welcome to the Vernachain documentation! This guide will help you get started with running nodes, using the CLI, and developing on Vernachain.

## Table of Contents

1. [Getting Started](getting-started.md)
   - Installation
   - Requirements
   - Quick Start

2. [Node Operation](node-operation.md)
   - Setting up a Node
   - Running a Bootstrap Node
   - Node Configuration
   - Network Participation

3. [CLI Tool](cli-tool.md)
   - Installation
   - Commands Reference
   - Examples

4. [Smart Contracts](smart-contracts.md)
   - Writing Contracts
   - Contract Deployment
   - Interacting with Contracts
   - Best Practices

5. [API Reference](api-reference.md)
   - Node API
   - SDK Usage
   - WebSocket Events

6. [Architecture](architecture.md)
   - Consensus Mechanism
   - Network Protocol
   - Sharding
   - State Management

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start a bootstrap node
python -m src.cli start-bootstrap --host localhost --port 5000

# Start a regular node
python -m src.cli start --host localhost --port 5001 --bootstrap-host localhost --bootstrap-port 5000

# Create a wallet
python -m src.wallet.cli create

# Send a transaction
python -m src.wallet.cli send FROM_ADDRESS TO_ADDRESS AMOUNT
```

## System Requirements

- Python 3.12.4+
- 2GB RAM minimum
- 10GB storage recommended
- Stable internet connection

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details. 