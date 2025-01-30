# Vernachain

<div align="center">

```ascii
                    ██╗   ██╗███████╗██████╗ ███╗   ██╗ █████╗ 
                    ██║   ██║██╔════╝██╔══██╗████╗  ██║██╔══██╗
                    ██║   ██║█████╗  ██████╔╝██╔██╗ ██║███████║
                    ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║
                     ╚████╔╝ ███████╗██║  ██║██║ ╚████║██║  ██║
                      ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                    ============================================
                           Next-Gen Blockchain Platform
                           ⬡ POWERED BY BRONZONTECH CLOUD ⬡
```

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12.4+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://vernachain.readthedocs.io/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/en/stable/)
[![Frontend](https://img.shields.io/badge/frontend-React%2018-blue.svg)](src/frontend/)
[![API](https://img.shields.io/badge/API-FastAPI-teal.svg)](src/api/)

A modern blockchain platform with Proof-of-Stake consensus, smart contracts, and advanced networking features.

[Getting Started](#installation) •
[Documentation](docs/) •
[Examples](examples/) •
[Contributing](CONTRIBUTING.md) •
[Changelog](CHANGELOG.md)

</div>

---

## 🌟 Key Features

### 🔗 Blockchain Core
- **Proof-of-Stake Consensus**
  - ⚡ Energy-efficient validation
  - 🔒 Secure staking mechanism
  - ⚔️ Slashing for malicious behavior
  - ⚖️ Proportional validator selection

- **Smart Contracts**
  - 🐍 Python-based contracts
  - ⛽ Gas metering system
  - 📡 Event emission
  - 🔄 Cross-contract calls

### 🌐 Network & Services
- **Multi-Service Architecture**
  - 🔄 Blockchain Node (port 5001)
  - 🌐 API Service (port 8000)
  - 📊 Explorer Backend (port 8001)
  - 💻 Frontend Dev Server (port 5173)

- **Advanced Networking**
  - 🌐 Kademlia DHT for peer discovery
  - 🔐 Secure P2P communication
  - ⚡ Asynchronous message handling
  - 🚀 NAT traversal

### 💼 Development Tools
- **Frontend SDK**
  - 🎨 Modern React/TypeScript interface
  - 🔄 Real-time data updates
  - 📊 Analytics dashboard
  - 🔐 Secure authentication

- **Backend Features**
  - 🚀 FastAPI-based REST API
  - 📡 WebSocket support
  - 🔒 JWT authentication
  - 📊 Advanced analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.12.4+
- Node.js 18+ (for frontend)
- 2GB RAM minimum
- Stable internet connection

### Installation

1. Clone the repository:
```bash
git clone https://github.com/BronzonTech-Cloud/vernachain.git
cd vernachain
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start all services in development mode:
```bash
python start.py --dev
```

This will start:
- Blockchain Node: http://localhost:5001
- API Service: http://localhost:8000
- Explorer Backend: http://localhost:8001
- Frontend Dev Server: http://localhost:5173

## ⚙️ Configuration

### Command Line Options
```bash
python start.py [OPTIONS]

Options:
  --dev                   Start in development mode
  --bootstrap             Start a bootstrap node
  --api-host HOST        API service host (default: localhost)
  --api-port PORT        API service port (default: 8000)
  --explorer-host HOST   Explorer host (default: localhost)
  --explorer-port PORT   Explorer port (default: 8001)
  --frontend-host HOST   Frontend host (default: localhost)
  --frontend-port PORT   Frontend port (default: 5173)
```

### Environment Variables
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_EXPLORER_URL=http://localhost:8001
VITE_NODE_URL=http://localhost:5001
VITE_API_KEY=your_api_key
```

## 📁 Project Structure
```
vernachain/
├── src/                      # Source code
│   ├── blockchain/          # Core blockchain implementation
│   │   ├── smart_contracts/ # Smart contract system
│   │   │   ├── vm.py       # Virtual machine implementation
│   │   │   ├── token.py    # Base token contract
│   │   │   ├── erc721.py   # NFT contract implementation
│   │   │   ├── erc1155.py  # Multi-token contract
│   │   │   ├── token_vesting.py # Token vesting contract
│   │   │   ├── token_swap.py    # Token swap contract
│   │   │   ├── governance.py    # Governance contract
│   │   │   ├── price_oracle.py  # Price oracle contract
│   │   │   └── factory.py  # Contract factory
│   │   ├── sharding.py     # Sharding implementation
│   │   ├── consensus.py    # Consensus mechanism
│   │   ├── transaction.py  # Transaction processing
│   │   └── block.py        # Block structure
│   ├── api/                # API implementation
│   │   ├── blockchain/     # Blockchain API endpoints
│   │   ├── explorer/       # Explorer API endpoints
│   │   └── websocket/      # WebSocket handlers
│   ├── auth/               # Authentication system
│   │   ├── service.py      # Auth service implementation
│   │   └── models.py       # Auth models
│   ├── bridge/             # Cross-chain bridge
│   │   ├── bridge_manager.py # Bridge management
│   │   └── contracts/      # Bridge contracts
│   ├── cli/                # Command-line interface
│   │   ├── commands/       # CLI command implementations
│   │   └── utils/          # CLI utilities
│   ├── consensus/          # Consensus implementation
│   │   ├── pos.py         # Proof of Stake
│   │   └── validator.py    # Validator management
│   ├── explorer/           # Blockchain explorer
│   │   ├── backend.py      # Explorer backend
│   │   └── api/           # Explorer API
│   ├── frontend/           # Web interface
│   │   ├── src/           # Frontend source
│   │   └── public/        # Static assets
│   ├── networking/         # P2P networking
│   │   ├── node.py        # Node implementation
│   │   └── protocol.py    # Network protocol
│   ├── sdk/                # Development SDK
│   │   ├── client.py      # SDK client
│   │   └── types.py       # SDK types
│   ├── tokens/             # Token management
│   │   ├── manager.py     # Token manager
│   │   └── standards.py   # Token standards
│   ├── utils/              # Utility functions
│   │   ├── crypto.py      # Cryptographic functions
│   │   ├── validation.py  # Data validation
│   │   └── serialization.py # Data serialization
│   └── wallet/             # Wallet implementation
│       ├── wallet.py      # Wallet core
│       └── keystore.py    # Key management
├── docs/                   # Documentation
│   ├── api-reference.md    # API documentation
│   ├── architecture.md     # System architecture
│   ├── getting-started.md  # Getting started guide
│   └── smart-contracts.md  # Smart contract guide
├── tests/                  # Test suite
│   ├── blockchain/         # Blockchain tests
│   ├── smart_contracts/    # Contract tests
│   └── integration/        # Integration tests
├── scripts/               # Development scripts
│   ├── setup.sh          # Setup script
│   └── test.sh          # Test runner
└── config/               # Configuration files
    ├── default.yaml     # Default configuration
    └── test.yaml       # Test configuration
```

## 🛠️ Development

### Running Tests
```bash
# Backend tests
pytest tests/

# Frontend tests
cd src/frontend
npm test
```

### Building Documentation
```bash
cd docs
mkdocs build
```

### API Documentation
- REST API: http://localhost:8000/docs
- WebSocket API: http://localhost:8000/ws/docs
- Explorer API: http://localhost:8001/docs

## 🔧 Troubleshooting

### Common Issues
1. **Services Won't Start**
   - Check port availability
   - Verify Python/Node.js versions
   - Check log files in `logs/`

2. **Frontend Issues**
   - Verify environment variables
   - Check browser console
   - Ensure all services are running

3. **API Connection Errors**
   - Check service URLs
   - Verify API key configuration
   - Check CORS settings

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [Frontend Documentation](src/frontend/README.md)
- [API Documentation](src/api/README.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

---

<div align="center">

Made with ❤️ by BronzonTech

</div>
