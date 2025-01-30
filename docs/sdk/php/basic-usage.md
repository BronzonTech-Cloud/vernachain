# Basic Usage Guide

## Client Initialization

```php
use Vernachain\SDK\VernachainClient;

$client = new VernachainClient([
    'node_url' => 'http://localhost:8545',
    'api_key' => 'your-api-key'
]);
```

## Account Operations

### Creating an Account
```php
// Generate new account
$account = $client->createAccount();
echo "Address: " . $account['address'] . "\n";
echo "Private Key: " . $account['private_key'] . "\n";

// Import existing account
$importedAccount = $client->importAccount($privateKey);
```

### Checking Balance
```php
$balance = $client->getBalance('0xYourAddress');
echo "Balance: " . $balance . "\n";

// Check balance in specific shard
$shardBalance = $client->getBalance('0xYourAddress', ['shard_id' => 1]);
```

## Basic Transactions

### Sending Transactions
```php
// Simple transfer
$tx = $client->createTransaction([
    'sender' => '0xSender',
    'recipient' => '0xRecipient',
    'amount' => '1000000000000000000', // 1 token
    'shard_id' => 0
]);

// Wait for confirmation
$receipt = $client->waitForTransaction($tx['hash']);
echo "Transaction confirmed: " . json_encode($receipt) . "\n";
```

### Transaction Status
```php
// Check transaction status
$status = $client->getTransactionStatus($tx['hash']);
echo "Status: " . $status . "\n";

// Get transaction details
$details = $client->getTransaction($tx['hash']);
echo "Details: " . json_encode($details) . "\n";
```

## Smart Contract Interaction

### Loading a Contract
```php
$contractAbi = [...]; // Your contract ABI
$contractAddress = '0xContractAddress';

$contract = $client->loadContract($contractAddress, $contractAbi);
```

### Reading Contract State
```php
// Call view function
$balance = $contract->methods->balanceOf('0xAddress')->call();
echo "Token Balance: " . $balance . "\n";

// Read multiple values
$name = $contract->methods->name()->call();
$symbol = $contract->methods->symbol()->call();
$decimals = $contract->methods->decimals()->call();
```

### Writing to Contract
```php
// Send transaction to contract
$result = $contract->methods->transfer('0xRecipient', '1000000000000000000')->send([
    'from' => '0xSender',
    'gas_limit' => 100000
]);

// Wait for confirmation
$receipt = $client->waitForTransaction($result['hash']);
```

## Event Handling

### Subscribing to Events
```php
// Listen for new blocks
$client->on('block', function($block) {
    echo "New block: " . $block['number'] . "\n";
});

// Listen for specific transactions
$client->on('transaction', function($tx) use ($myAddress) {
    if ($tx['sender'] === $myAddress) {
        echo "My transaction: " . json_encode($tx) . "\n";
    }
});
```

### Contract Events
```php
// Listen for contract events
$contract->events->Transfer()
    ->subscribe(function($event) {
        echo "Transfer: " . json_encode([
            'from' => $event['returnValues']['from'],
            'to' => $event['returnValues']['to'],
            'value' => $event['returnValues']['value']
        ]) . "\n";
    }, function($error) {
        echo "Error: " . $error->getMessage() . "\n";
    });
```

## Error Handling

### Basic Error Handling
```php
try {
    $result = $client->createTransaction([/* ... */]);
} catch (InsufficientFundsException $e) {
    echo "Not enough funds: " . $e->getMessage() . "\n";
} catch (NetworkException $e) {
    echo "Network issue: " . $e->getMessage() . "\n";
} catch (Exception $e) {
    echo "Unknown error: " . $e->getMessage() . "\n";
}
```

### Transaction Error Handling
```php
try {
    $tx = $contract->methods->transfer($recipient, $amount)->send([
        'from' => $sender,
        'gas_limit' => 100000
    ]);
    
    $receipt = $client->waitForTransaction($tx['hash']);
    if ($receipt['status'] === 'failed') {
        echo "Transaction failed: " . $receipt['error'] . "\n";
    }
} catch (Exception $e) {
    echo "Transaction error: " . $e->getMessage() . "\n";
}
```

## Utility Functions

### Gas Estimation
```php
// Estimate transaction gas
$gasEstimate = $client->estimateGas([
    'sender' => '0xSender',
    'recipient' => '0xRecipient',
    'amount' => '1000000000000000000'
]);

// Estimate contract method gas
$methodGas = $contract->methods->transfer($recipient, $amount)
    ->estimateGas(['from' => $sender]);
```

### Network Information
```php
// Get network status
$status = $client->getNodeStatus();
echo "Node status: " . json_encode($status) . "\n";

// Get current gas price
$gasPrice = $client->getGasPrice();
echo "Current gas price: " . $gasPrice . "\n";
```

## Best Practices

### Connection Management
```php
// Check connection before operations
if ($client->isConnected()) {
    // Proceed with operations
} else {
    // Handle connection issue
}

// Cleanup
$client->disconnect();
```

### Transaction Building
```php
// Build transaction with proper gas settings
$tx = $client->createTransaction([
    'sender' => '0xSender',
    'recipient' => '0xRecipient',
    'amount' => '1000000000000000000',
    'gas_price' => $client->getGasPrice(),
    'gas_limit' => $gasEstimate * 1.2 // Add 20% buffer
]);
```

### Async Operations
```php
// Using promises for concurrent operations
$promises = [
    $client->getBalance($address),
    $client->getTransactions($address)
];

$results = Promise\all($promises)->wait();
[$balance, $transactions] = $results;

echo "Balance: " . $balance . "\n";
echo "Transaction count: " . count($transactions) . "\n";
```

### Memory Management
```php
// Handle large datasets
$iterator = $client->getTransactionIterator($address);
foreach ($iterator as $tx) {
    // Process transaction
    // Memory is freed after each iteration
}

// Clear event listeners when done
$client->removeAllListeners();
``` 