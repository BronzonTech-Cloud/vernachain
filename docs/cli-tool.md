# CLI Tool Documentation

The Vernachain CLI tool provides a command-line interface for interacting with the blockchain network, managing wallets, and performing various operations.

## Table of Contents
- [Installation](#installation)
- [Global Options](#global-options)
- [Node Commands](#node-commands)
- [Wallet Commands](#wallet-commands)
- [Transaction Commands](#transaction-commands)
- [Validator Commands](#validator-commands)
- [Smart Contract Commands](#smart-contract-commands)

## Installation

The CLI tool is included with Vernachain. After installing the main package:
```bash
pip install -r requirements.txt
```

## Global Options

Common options available for all commands:
```bash
--verbose       Enable verbose output
--json         Output in JSON format
--config FILE  Specify custom config file
--help        Show help message
```

## Node Commands

### Start Bootstrap Node
```bash
python -m src.cli start-bootstrap [OPTIONS]
  --host TEXT          Host address (default: localhost)
  --port INTEGER       Port number (default: 5000)
  --max-peers INTEGER  Maximum number of peers (default: 50)
```

### Start Regular Node
```bash
python -m src.cli start [OPTIONS]
  --host TEXT              Host address (default: localhost)
  --port INTEGER           Port number (default: 5001)
  --bootstrap-host TEXT    Bootstrap node host
  --bootstrap-port INTEGER Bootstrap node port
  --validator BOOLEAN      Run as validator
```

### Node Status
```bash
python -m src.cli status
```

### Node Management
```bash
python -m src.cli recover     # Recover from crash
python -m src.cli resync      # Force resync
python -m src.cli clear-peers # Clear peer database
```

## Wallet Commands

### Create Wallet
```bash
python -m src.wallet.cli create [OPTIONS]
  -l, --label TEXT  Wallet label
  -p, --password    Set wallet password
```

### List Wallets
```bash
python -m src.wallet.cli list
```

### Check Balance
```bash
python -m src.wallet.cli balance [OPTIONS]
  --address TEXT  Specific address (optional)
```

### Import/Export
```bash
python -m src.wallet.cli import --file PATH
python -m src.wallet.cli export --file PATH
```

## Transaction Commands

### Send Transaction
```bash
python -m src.wallet.cli send [OPTIONS]
  --to TEXT      Recipient address
  --amount FLOAT Amount to send
  --fee FLOAT    Transaction fee (optional)
  --data TEXT    Additional data (optional)
```

### View Transaction
```bash
python -m src.cli tx [OPTIONS]
  --hash TEXT    Transaction hash
```

### List Transactions
```bash
python -m src.cli tx list [OPTIONS]
  --address TEXT Address to filter by
  --limit INT    Number of transactions
  --pending      Show pending transactions
```

## Validator Commands

### Stake Tokens
```bash
python -m src.wallet.cli stake [OPTIONS]
  --amount FLOAT Amount to stake
```

### Unstake Tokens
```bash
python -m src.wallet.cli unstake [OPTIONS]
  --amount FLOAT Amount to unstake
```

### Validator Status
```bash
python -m src.cli validator status [OPTIONS]
  --address TEXT Validator address
```

### List Validators
```bash
python -m src.cli validator list [OPTIONS]
  --active       Show only active validators
```

## Smart Contract Commands

### Deploy Contract
```bash
python -m src.cli deploy-contract [OPTIONS]
  --file PATH    Contract file path
  --args TEXT    Constructor arguments
  --gas FLOAT    Gas limit
```

### Call Contract
```bash
python -m src.cli call-contract [OPTIONS]
  --address TEXT Contract address
  --function TEXT Function name
  --args TEXT    Function arguments
  --gas FLOAT    Gas limit
```

### View Contract
```bash
python -m src.cli contract [OPTIONS]
  --address TEXT Contract address
  --abi         Show contract ABI
```

## Examples

1. Start a node and become a validator:
```bash
python -m src.cli start --validator --bootstrap-host localhost --bootstrap-port 5000
python -m src.wallet.cli stake --amount 1000
```

2. Send a transaction:
```bash
python -m src.wallet.cli send --to 0x123... --amount 10.5
```

3. Deploy and interact with a contract:
```bash
# Deploy
python -m src.cli deploy-contract --file token.py --args "MyToken,MTK,1000000"

# Call contract
python -m src.cli call-contract --address 0x456... --function transfer --args "0x789...,100"
```

## Error Handling

Common error codes and their meanings:
- `E001`: Invalid address format
- `E002`: Insufficient balance
- `E003`: Transaction failed
- `E004`: Network error
- `E005`: Invalid contract

For detailed error descriptions, use the `--verbose` flag.

## Configuration

The CLI can be configured using:
1. Command line arguments
2. Environment variables
3. Configuration file (default: `~/.vernachain/config.yaml`)

Priority: Arguments > Environment > Config File

For more detailed information about specific commands, use the `--help` flag with any command. 