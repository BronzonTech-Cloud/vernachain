# Node Operation Guide

This guide explains how to operate Vernachain nodes, including bootstrap nodes and regular nodes.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Node Types](#node-types)
- [Configuration Options](#configuration-options)
- [Running Nodes](#running-nodes)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before running a node, ensure you have:
- Python 3.12.4 or higher installed
- Required dependencies from `requirements.txt`
- At least 2GB of RAM available
- Stable internet connection
- Open ports for P2P communication

## Node Types

### Bootstrap Node
- Acts as an entry point for new nodes joining the network
- Maintains a list of active peers
- Helps with initial peer discovery
- Should be run on a stable, always-on system

### Regular Node
- Participates in block validation and consensus
- Processes transactions and maintains the blockchain
- Can become a validator by staking tokens
- Connects to bootstrap nodes for peer discovery

## Configuration Options

### Common Options
- `--host`: Node's host address (default: localhost)
- `--port`: Node's port number (default: 5000/5001)
- `--data-dir`: Directory for blockchain data
- `--log-level`: Logging verbosity (debug/info/warning/error)

### Bootstrap Node Options
```bash
python -m src.cli start-bootstrap [OPTIONS]
  --host TEXT          Host address (default: localhost)
  --port INTEGER       Port number (default: 5000)
  --max-peers INTEGER  Maximum number of peers (default: 50)
```

### Regular Node Options
```bash
python -m src.cli start [OPTIONS]
  --host TEXT              Host address (default: localhost)
  --port INTEGER           Port number (default: 5001)
  --bootstrap-host TEXT    Bootstrap node host
  --bootstrap-port INTEGER Bootstrap node port
  --validator BOOLEAN      Run as validator (requires stake)
```

## Running Nodes

### Using the Startup Script
The easiest way to run nodes is using the startup script:

1. Development mode with all components:
```bash
./start.sh --dev
```

2. Production mode with bootstrap node:
```bash
./start.sh --bootstrap
```

3. Custom configuration:
```bash
./start.sh --bootstrap \
    --node-port 5001 \
    --api-port 8000 \
    --explorer-port 8001
```

### Manual Node Operation

1. Start a bootstrap node:
```bash
python -m src.cli start-bootstrap --host localhost --port 5000
```

2. Start a regular node:
```bash
python -m src.cli start \
    --host localhost \
    --port 5001 \
    --bootstrap-host localhost \
    --bootstrap-port 5000
```

## Monitoring

### Node Status
Check node status using the CLI:
```bash
python -m src.cli status
```

This shows:
- Connection status
- Number of peers
- Blockchain height
- Validator status (if applicable)
- System resources usage

### Logs
Logs are stored in the data directory:
- `node.log`: General node operations
- `consensus.log`: Consensus-related events
- `network.log`: P2P networking events

### Metrics
Monitor node performance through the API:
- `GET /api/v1/node/stats`: Node statistics
- `GET /api/v1/node/peers`: Connected peers
- `GET /api/v1/node/blocks`: Recent blocks
- `GET /api/v1/node/transactions`: Pending transactions

## Troubleshooting

### Common Issues

1. Connection Failed
- Verify bootstrap node is running
- Check firewall settings
- Ensure ports are open

2. Peer Discovery Issues
- Verify bootstrap node address
- Check network connectivity
- Ensure sufficient peer slots available

3. Validation Errors
- Verify stake amount
- Check validator configuration
- Ensure node is synced

4. Performance Issues
- Monitor system resources
- Check disk space
- Adjust max peers if needed

### Recovery Steps

1. Node Crash Recovery
```bash
python -m src.cli recover
```

2. Force Resync
```bash
python -m src.cli resync
```

3. Clear Peer Database
```bash
python -m src.cli clear-peers
```

For additional support, check the [troubleshooting guide](troubleshooting.md) or open an issue on GitHub.