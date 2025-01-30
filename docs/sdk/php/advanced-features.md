 # Advanced Features Guide

## Cross-Shard Operations

### Cross-Shard Transfers
```php
// Initiate cross-shard transfer
$transfer = $client->initiateCrossShardTransfer([
    'from_shard' => 0,
    'to_shard' => 1,
    'transaction' => [
        'sender' => '0xSender',
        'recipient' => '0xRecipient',
        'amount' => '1000000000000000000',
        'gas_price' => 1.5,
        'gas_limit' => 21000
    ]
]);

// Monitor transfer status
$status = $client->getBridgeTransferStatus($transfer['transfer_id']);
while (!in_array($status['status'], ['completed', 'failed'])) {
    echo "Status: " . $status['status'] . "\n";
    sleep(5);
    $status = $client->getBridgeTransferStatus($transfer['transfer_id']);
}
```

### State Verification
```php
// Get state proof
$proof = $client->getStateProof([
    'shard_id' => 1,
    'address' => '0xContract',
    'key' => 'balance'
]);

// Verify state across shards
$isValid = $client->verifyStateProof($proof);
```

## Batch Operations

### Transaction Batching
```php
// Create batch transaction
$batch = $client->createBatch([
    [
        'method' => 'createTransaction',
        'params' => [
            'sender' => '0xSender1',
            'recipient' => '0xRecipient1',
            'amount' => '1000000000000000000'
        ]
    ],
    [
        'method' => 'deployContract',
        'params' => [
            'code' => $contractCode,
            'constructor_args' => $args
        ]
    ]
]);

// Execute batch
$results = $batch->execute();
```

### Contract Batch Calls
```php
// Batch contract calls
$calls = [
    $contract->methods->balanceOf('0xAddress1'),
    $contract->methods->balanceOf('0xAddress2'),
    $contract->methods->totalSupply()
];

$results = $contract->batch($calls)->call();
```

## Advanced Contract Features

### Contract Deployment
```php
// Deploy with libraries
$deployment = $client->deployContract([
    'code' => $contractCode,
    'constructor_args' => $args,
    'libraries' => [
        'LibraryName' => '0xLibraryAddress'
    ],
    'gas_limit' => 4000000
]);

// Deploy proxy contract
$proxy = $client->deployProxy([
    'implementation' => '0xImplementationAddress',
    'admin' => '0xAdminAddress',
    'data' => $initializerData
]);
```

### Contract Upgrades
```php
// Upgrade proxy implementation
$upgrade = $client->upgradeProxy([
    'proxy' => '0xProxyAddress',
    'implementation' => '0xNewImplementationAddress',
    'data' => $migrationData
]);

// Verify implementation
$implementation = $client->getProxyImplementation('0xProxyAddress');
```

## Advanced Event Handling

### Custom Event Filters
```php
// Create custom event filter
$filter = $contract->createFilter([
    'event' => 'Transfer',
    'fromBlock' => 'latest',
    'filter' => [
        'from' => '0xSender',
        'value' => ['gte' => '1000000000000000000']
    ]
]);

// Watch filter
$filter->watch(function($events) {
    foreach ($events as $event) {
        echo "Large transfer: " . json_encode($event) . "\n";
    }
});
```

### Event Aggregation
```php
// Aggregate events
$transfers = $contract->events->Transfer([
    'fromBlock' => $startBlock,
    'toBlock' => $endBlock
])->aggregate(function($events) {
    return array_reduce($events, function($sum, $event) {
        return $sum + $event['returnValues']['value'];
    }, 0);
});
```

## Performance Optimization

### Connection Pooling
```php
// Create connection pool
$pool = new ConnectionPool([
    'min' => 5,
    'max' => 20,
    'node_urls' => [
        'http://node1:8545',
        'http://node2:8545'
    ]
]);

// Get client from pool
$client = $pool->getClient();
```

### Caching
```php
// Setup cache
$cache = new Cache([
    'driver' => 'redis',
    'connection' => 'default',
    'ttl' => 3600
]);

// Use cache with client
$client->setCache($cache);

// Cached contract call
$balance = $contract->methods->balanceOf('0xAddress')
    ->cache(60)
    ->call();
```

## Security Features

### Transaction Signing
```php
// Sign transaction offline
$signedTx = $client->signTransaction([
    'sender' => '0xSender',
    'recipient' => '0xRecipient',
    'amount' => '1000000000000000000',
    'nonce' => $nonce,
    'private_key' => $privateKey
]);

// Send signed transaction
$result = $client->sendSignedTransaction($signedTx);
```

### Message Signing
```php
// Sign message
$signature = $client->signMessage($message, $privateKey);

// Verify signature
$isValid = $client->verifySignature($message, $signature, $address);
```

## Debugging and Monitoring

### Transaction Tracing
```php
// Trace transaction
$trace = $client->traceTransaction($txHash, [
    'tracer' => 'callTracer',
    'timeout' => '5s'
]);

// Get transaction receipt with logs
$receipt = $client->getTransactionReceipt($txHash);
foreach ($receipt['logs'] as $log) {
    echo "Log: " . json_encode($log) . "\n";
}
```

### Performance Monitoring
```php
// Enable performance monitoring
$client->enableProfiling();

// Get performance metrics
$metrics = $client->getMetrics();
echo "Average response time: " . $metrics['avg_response_time'] . "ms\n";
echo "Request count: " . $metrics['request_count'] . "\n";

// Export metrics
$client->exportMetrics('prometheus', 'metrics.txt');
```

## Error Recovery

### Automatic Retry
```php
// Configure retry strategy
$client->setRetryStrategy([
    'max_attempts' => 3,
    'initial_delay' => 1000,
    'max_delay' => 5000,
    'backoff_factor' => 2,
    'retryable_errors' => [
        NetworkException::class,
        TimeoutException::class
    ]
]);

// Operation with retry
$result = $client->withRetry(function() use ($client) {
    return $client->createTransaction([/* ... */]);
});
```

### State Recovery
```php
// Save transaction state
$state = $client->saveTransactionState($tx);

// Recover transaction
$recoveredTx = $client->recoverTransaction($state);
if ($recoveredTx['status'] === 'pending') {
    $client->retryTransaction($recoveredTx);
}
```