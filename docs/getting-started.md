# Getting Started with Vernachain

This guide will help you set up and run your first Vernachain node, create a wallet, and perform basic operations.

## Table of Contents
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Running the Network](#running-the-network)
- [Creating a Wallet](#creating-a-wallet)
- [Basic Operations](#basic-operations)
- [Next Steps](#next-steps)

## Installation

1. System Requirements:
   - Python 3.12.4 or higher
   - Node.js and npm (for frontend)
   - 2GB RAM minimum
   - 10GB storage recommended
   - Stable internet connection

2. Clone the Repository:
   ```bash
   git clone https://github.com/BronzonTech-Cloud/vernachain.git
   cd vernachain
   ```

3. Install Dependencies:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Install frontend dependencies
   cd src/frontend && npm install && cd ../..
   ```

## Initial Setup

1. Environment Configuration:
   - Ensure required ports are available (default: 5000, 5001, 8000, 8001, 3000)
   - Configure firewall rules if needed
   - Set up environment variables (optional)

2. Directory Structure:
   ```
   vernachain/
   ├── src/              # Source code
   ├── docs/             # Documentation
   ├── tests/            # Test files
   ├── requirements.txt  # Python dependencies
   └── start.sh/bat      # Startup scripts
   ```

## Running the Network

1. Development Mode (includes hot reloading):
   ```bash
   ./start.sh --dev      # Unix systems
   start.bat --dev       # Windows
   ```

2. Production Mode with Bootstrap Node:
   ```bash
   ./start.sh --bootstrap
   ```

3. Custom Configuration:
   ```bash
   ./start.sh --bootstrap \
       --node-port 5001 \
       --api-port 8000 \
       --explorer-port 8001
   ```

## Creating a Wallet

1. Create a New Wallet:
   ```bash
   python -m src.wallet.cli create -l "My Wallet"
   ```

2. Check Wallet Balance:
   ```bash
   python -m src.wallet.cli balance
   ```

3. List Available Wallets:
   ```bash
   python -m src.wallet.cli list
   ```

## Basic Operations

1. Access Components:
   - Frontend Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Explorer API: http://localhost:8001/docs

2. Send Transactions:
   ```bash
   python -m src.wallet.cli send --to ADDRESS --amount VALUE
   ```

3. Stake Tokens (to become a validator):
   ```bash
   python -m src.wallet.cli stake --amount VALUE
   ```

4. Deploy Smart Contract:
   ```bash
   python -m src.cli deploy-contract --file path/to/contract.py
   ```

## Next Steps

1. Explore Advanced Features:
   - [Node Operation Guide](node-operation.md)
   - [Smart Contracts Guide](smart-contracts.md)
   - [API Reference](api-reference.md)

2. Development Resources:
   - Join our community
   - Check example projects
   - Read the architecture documentation

3. Best Practices:
   - Regular backups
   - Security considerations
   - Performance optimization

For more detailed information, refer to the specific documentation sections or join our community channels. 