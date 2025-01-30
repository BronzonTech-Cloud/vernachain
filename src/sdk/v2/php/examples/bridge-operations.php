<?php

require_once __DIR__ . '/../vendor/autoload.php';

use Vernachain\SDK\VernachainClient;

try {
    $client = new VernachainClient([
        'node_url' => 'http://localhost:8545',
        'api_key' => 'your-api-key'
    ]);

    // Lock tokens in source chain
    $lockRequest = [
        'token_address' => '0x1234...', // ERC20 token address
        'amount' => '1000000000000000000', // 1 token with 18 decimals
        'target_chain' => 'ethereum',
        'recipient' => '0x5678...', // recipient address on target chain
        'shard_id' => 0,
        'gas_price' => 1.5,
        'gas_limit' => 100000
    ];

    $lockResult = $client->lockTokens($lockRequest);
    echo "Tokens locked. Transaction hash: {$lockResult['transaction_hash']}\n";
    echo "Bridge transfer ID: {$lockResult['bridge_transfer_id']}\n";

    // Monitor bridge transfer status
    $bridgeStatus = $client->getBridgeTransferStatus($lockResult['bridge_transfer_id']);
    while (!in_array($bridgeStatus['status'], ['completed', 'failed'])) {
        echo "Bridge transfer status: {$bridgeStatus['status']}\n";
        echo "Confirmations: {$bridgeStatus['confirmations']}/{$bridgeStatus['required_confirmations']}\n";
        
        sleep(10); // Wait 10 seconds
        $bridgeStatus = $client->getBridgeTransferStatus($lockResult['bridge_transfer_id']);
    }

    echo "Final bridge transfer status: {$bridgeStatus['status']}\n";
    if ($bridgeStatus['status'] === 'completed') {
        echo "Target chain transaction hash: {$bridgeStatus['target_transaction_hash']}\n";
    }

    // Example of unlocking tokens (receiving from another chain)
    $pendingTransfers = $client->getPendingBridgeTransfers('ethereum');
    foreach ($pendingTransfers as $transfer) {
        if ($transfer['status'] === 'pending_unlock') {
            $unlockResult = $client->unlockTokens([
                'bridge_transfer_id' => $transfer['bridge_transfer_id'],
                'proof' => $transfer['proof'],
                'shard_id' => 0,
                'gas_price' => 1.5,
                'gas_limit' => 150000
            ]);
            echo "Tokens unlocked. Transaction hash: {$unlockResult['transaction_hash']}\n";
        }
    }

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
} 