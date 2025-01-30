# Testing Guide

## Overview
This guide covers testing practices for the Vernachain project, including unit tests, integration tests, and end-to-end testing.

## Test Structure

### Directory Layout
```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── e2e/                  # End-to-end tests
├── fixtures/             # Test fixtures
└── utils/               # Test utilities
```

## Unit Testing

### Writing Unit Tests
```typescript
// Example unit test for transaction validation
import { validateTransaction } from '../src/utils/validation';

describe('Transaction Validation', () => {
    it('should validate correct transaction', () => {
        const tx = {
            sender: '0x1234...',
            recipient: '0x5678...',
            amount: '1000000000000000000',
            shard_id: 0
        };
        expect(validateTransaction(tx)).toBe(true);
    });

    it('should reject invalid amount', () => {
        const tx = {
            sender: '0x1234...',
            recipient: '0x5678...',
            amount: '-1',
            shard_id: 0
        };
        expect(() => validateTransaction(tx)).toThrow('Invalid amount');
    });
});
```

### Running Unit Tests
```bash
# Run all unit tests
npm run test:unit

# Run specific test file
npm run test:unit -- transaction.test.ts

# Run with coverage
npm run test:unit:coverage
```

## Integration Testing

### Setting Up Integration Tests
```typescript
// Example integration test setup
import { TestEnvironment } from '../utils/test-env';

describe('Cross-Shard Operations', () => {
    let env: TestEnvironment;

    beforeAll(async () => {
        env = await TestEnvironment.create({
            shards: 2,
            validators: 4
        });
    });

    afterAll(async () => {
        await env.cleanup();
    });

    it('should transfer tokens across shards', async () => {
        const result = await env.client.initiateCrossShardTransfer({
            from_shard: 0,
            to_shard: 1,
            transaction: {
                sender: env.accounts[0],
                recipient: env.accounts[1],
                amount: '1000000000000000000'
            }
        });
        expect(result.status).toBe('completed');
    });
});
```

### Running Integration Tests
```bash
# Run all integration tests
npm run test:integration

# Run specific integration test
npm run test:integration -- cross-shard.test.ts
```

## End-to-End Testing

### E2E Test Example
```typescript
// Example E2E test
describe('Full Transaction Flow', () => {
    it('should complete full transaction lifecycle', async () => {
        // 1. Deploy contract
        const contract = await client.deployContract({
            code: contractCode,
            constructor_args: []
        });

        // 2. Perform transaction
        const tx = await contract.methods.transfer(recipient, amount).send({
            from: sender,
            gas_limit: 100000
        });

        // 3. Verify transaction
        const receipt = await client.waitForTransaction(tx.hash);
        expect(receipt.status).toBe('success');

        // 4. Check final state
        const balance = await contract.methods.balanceOf(recipient).call();
        expect(balance).toBe(amount);
    });
});
```

### Running E2E Tests
```bash
# Run all E2E tests
npm run test:e2e

# Run specific E2E test
npm run test:e2e -- transaction-flow.test.ts
```

## Performance Testing

### Load Test Example
```typescript
import { LoadTest } from '../utils/load-test';

describe('Performance Tests', () => {
    it('should handle high transaction volume', async () => {
        const loadTest = new LoadTest({
            duration: '5m',
            rampUp: '30s',
            targetTPS: 1000
        });

        const results = await loadTest.run(async () => {
            await client.createTransaction({
                sender: generateAddress(),
                recipient: generateAddress(),
                amount: '1000000000000000000'
            });
        });

        expect(results.successRate).toBeGreaterThan(0.99);
        expect(results.averageLatency).toBeLessThan(1000);
    });
});
```

### Running Performance Tests
```bash
# Run performance tests
npm run test:performance

# Run with specific configuration
npm run test:performance -- --config high-load.json
```

## Test Utilities

### Mocking
```typescript
// Example mock implementation
jest.mock('../src/client', () => ({
    VernachainClient: jest.fn().mockImplementation(() => ({
        createTransaction: jest.fn().mockResolvedValue({
            hash: '0x1234...',
            status: 'success'
        })
    }))
}));
```

### Test Fixtures
```typescript
// Example fixture
export const testTransactions = [
    {
        sender: '0x1234...',
        recipient: '0x5678...',
        amount: '1000000000000000000',
        shard_id: 0
    },
    // More test cases...
];
```

## Continuous Integration

### CI Pipeline
```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: |
          npm run test:unit
          npm run test:integration
          npm run test:e2e
```

## Best Practices

### Testing Guidelines
1. Write tests before code (TDD)
2. Keep tests focused and isolated
3. Use meaningful test descriptions
4. Implement proper cleanup
5. Maintain test coverage

### Code Coverage
```bash
# Generate coverage report
npm run coverage

# View detailed coverage
npm run coverage:report
```

## Troubleshooting

### Common Issues
1. Test timeouts
2. Network-related failures
3. State contamination
4. Resource cleanup

### Solutions
- Increase timeout limits
- Mock network calls
- Reset state between tests
- Implement proper teardown 