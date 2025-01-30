<?php

require_once __DIR__ . '/../vendor/autoload.php';

use Vernachain\SDK\VernachainClient;

try {
    $client = new VernachainClient([
        'node_url' => 'http://localhost:8545',
        'api_key' => 'your-api-key'
    ]);

    // Example contract ABI (ERC20 token)
    $contractAbi = [
        [
            'constant' => true,
            'inputs' => [['name' => '_owner', 'type' => 'address']],
            'name' => 'balanceOf',
            'outputs' => [['name' => 'balance', 'type' => 'uint256']],
            'type' => 'function'
        ],
        [
            'constant' => false,
            'inputs' => [
                ['name' => '_to', 'type' => 'address'],
                ['name' => '_value', 'type' => 'uint256']
            ],
            'name' => 'transfer',
            'outputs' => [['name' => '', 'type' => 'bool']],
            'type' => 'function'
        ]
    ];

    $contractAddress = '0x1234...'; // Your contract address
    $contract = $client->loadContract($contractAddress, $contractAbi);

    // Read operation (no gas needed)
    $balance = $contract->methods->balanceOf('0x5678...')->call();
    echo "Token balance: {$balance}\n";

    // Write operation (requires gas)
    $transferAmount = '1000000000000000000'; // 1 token with 18 decimals
    $transferResult = $contract->methods->transfer('0x9abc...', $transferAmount)->send([
        'from' => '0x5678...',
        'shard_id' => 0,
        'gas_price' => 1.5,
        'gas_limit' => 60000
    ]);

    echo "Transfer transaction hash: {$transferResult['transaction_hash']}\n";
    echo "Transaction status: {$transferResult['status']}\n";

    // Wait for transaction confirmation
    $receipt = $client->waitForTransaction($transferResult['transaction_hash']);
    echo "Transaction confirmed in block: {$receipt['block_number']}\n";
    echo "Gas used: {$receipt['gas_used']}\n";

    // Event listening
    $events = $contract->getPastEvents('Transfer', [
        'fromBlock' => $receipt['block_number'],
        'toBlock' => $receipt['block_number']
    ]);

    foreach ($events as $event) {
        echo "Transfer event:\n";
        echo "  From: {$event['returnValues']['from']}\n";
        echo "  To: {$event['returnValues']['to']}\n";
        echo "  Value: {$event['returnValues']['value']}\n";
    }

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}