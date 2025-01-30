 # Installation Guide

## System Requirements

### Hardware Requirements
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 100GB+ SSD recommended
- Network: Stable internet connection

### Software Requirements
- Python 3.8 or higher
- pip package manager
- Git
- Operating System: Linux, macOS, or Windows

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/BronzonTech-Cloud/vernachain.git
cd vernachain
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Configuration
```bash
# Copy example configuration
cp config.example.yaml config.yaml

# Edit configuration file
nano config.yaml
```

Example configuration:
```yaml
node:
  host: localhost
  port: 8000
  ws_port: 8001

blockchain:
  network_id: 1
  shard_count: 4
  block_time: 5
  gas_limit: 10000000

consensus:
  min_stake: 1000
  validator_limit: 100
  block_reward: 10

security:
  private_key_file: keys/private.pem
  public_key_file: keys/public.pem
```

### 5. Initialize Node
```bash
# Generate keys
python -m src.cli init-keys

# Initialize blockchain data
python -m src.cli init-chain
```

## Validator Setup

### 1. Stake Tokens
```bash
python -m src.cli stake --amount 1000
```

### 2. Configure Validator
```bash
python -m src.cli validator-config \
    --name "My Validator" \
    --website "https://validator.example.com" \
    --description "Reliable validator node"
```

### 3. Start Validator Node
```bash
python -m src.cli start-validator
```

## Development Setup

### 1. Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### 2. Setup Pre-commit Hooks
```bash
pre-commit install
```

### 3. Run Tests
```bash
pytest tests/
```

## Docker Installation

### 1. Build Image
```bash
docker build -t vernachain .
```

### 2. Run Container
```bash
docker run -d \
    --name vernachain-node \
    -p 8000:8000 \
    -p 8001:8001 \
    -v $(pwd)/data:/app/data \
    vernachain
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check ports
netstat -tulpn | grep "8000\|8001"

# Kill process using port
kill $(lsof -t -i:8000)
```

#### Permission Issues
```bash
# Fix permissions
chmod +x scripts/*.sh
sudo chown -R $USER:$USER data/
```

#### Database Issues
```bash
# Reset blockchain data
python -m src.cli reset-chain
```

## Next Steps
- Follow the [Getting Started Guide](getting-started.md)
- Set up a [Development Environment](development.md)
- Learn about [Smart Contracts](smart-contracts.md)