# Development Guide

## Development Environment Setup

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- Git
- Docker (optional, for local testnet)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/BronzonTech-Cloud/vernachain
cd vernachain

# Install dependencies
npm install        # For JavaScript/TypeScript development
pip install -r requirements.txt  # For Python development

# Setup development environment
npm run setup-dev
```

## Project Structure
```
vernachain/
├── src/
│   ├── blockchain/     # Core blockchain implementation
│   ├── sdk/           # Client SDKs
│   │   ├── v2/
│   │   │   ├── javascript/
│   │   │   └── php/
│   ├── api/          # API implementation
│   └── utils/        # Shared utilities
├── tests/           # Test suites
├── docs/           # Documentation
└── scripts/        # Development scripts
```

## Development Workflow

### 1. Branch Management
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Keep branch updated
git fetch origin
git rebase origin/main
```

### 2. Code Style
- Follow TypeScript/JavaScript style guide
- Use ESLint and Prettier
- Run style checks:
```bash
npm run lint
npm run format
```

### 3. Local Development
```bash
# Start local development node
npm run dev-node

# Run development environment
npm run dev

# Watch for changes
npm run watch
```

## SDK Development

### JavaScript/TypeScript SDK
```typescript
// Example SDK feature implementation
export class VernachainClient {
    async implementNewFeature(params: FeatureParams): Promise<FeatureResult> {
        // Implementation
        const result = await this.request('POST', '/api/feature', params);
        return FeatureResultSchema.parse(result);
    }
}
```

### Testing SDK Changes
```bash
# Run SDK tests
npm run test:sdk

# Test specific feature
npm run test:sdk -- --grep "feature-name"
```

## API Development

### Adding New Endpoints
1. Define route in `src/api/routes/`
2. Implement controller in `src/api/controllers/`
3. Add validation in `src/api/validators/`
4. Update API documentation

### Example Implementation
```typescript
// Route definition
router.post('/api/feature', validateFeature, featureController);

// Controller implementation
export async function featureController(req: Request, res: Response) {
    try {
        const result = await processFeature(req.body);
        return res.json(result);
    } catch (error) {
        handleError(error, res);
    }
}
```

## Smart Contract Development

### Contract Development
```solidity
// Example smart contract
contract VernaFeature {
    // State variables
    mapping(address => uint256) public features;

    // Events
    event FeatureUpdated(address indexed user, uint256 value);

    // Functions
    function updateFeature(uint256 value) external {
        features[msg.sender] = value;
        emit FeatureUpdated(msg.sender, value);
    }
}
```

### Contract Testing
```javascript
describe('VernaFeature', () => {
    it('should update feature value', async () => {
        const contract = await deployContract('VernaFeature');
        await contract.updateFeature(123);
        const value = await contract.features(owner.address);
        expect(value).to.equal(123);
    });
});
```

## Debugging

### Logging
```typescript
// Use structured logging
logger.info('Processing feature', {
    feature_id: id,
    params: requestParams,
    timestamp: new Date()
});
```

### Debugging Tools
- VS Code debugger configuration
- Chrome DevTools for frontend
- Postman for API testing

## Performance Optimization

### Profiling
```bash
# Run performance tests
npm run perf-test

# Generate profile report
npm run profile
```

### Best Practices
1. Use async/await properly
2. Implement caching where appropriate
3. Optimize database queries
4. Use proper indexing

## Deployment

### Building for Production
```bash
# Build all components
npm run build

# Build specific component
npm run build:sdk
npm run build:api
```

### Configuration
```typescript
// Example configuration
export const config = {
    node: {
        port: process.env.NODE_PORT || 8545,
        host: process.env.NODE_HOST || 'localhost'
    },
    security: {
        apiKey: process.env.API_KEY,
        rateLimit: process.env.RATE_LIMIT || 100
    }
};
```

## Contributing Guidelines

### Pull Requests
1. Create descriptive PR title
2. Fill out PR template
3. Include tests
4. Update documentation
5. Ensure CI passes

### Code Review
- Review guidelines
- Performance considerations
- Security checks
- Documentation updates 