<?php

require_once __DIR__ . '/../vendor/autoload.php';

use Vernachain\SDK\Client;
use Vernachain\SDK\Models\TransactionRequest;
use Vernachain\SDK\Models\CrossShardTransferRequest;

$client = new Client([
    'nodeUrl' => 'http://localhost:8545',
    'apiKey' => 'your-api-key'
]);

try {
    // Create a cross-shard transfer
    $transferRequest = new CrossShardTransferRequest([
        'fromShard' => 0,
        'toShard' => 1,
        'transaction' => new TransactionRequest([
            'sender' => '0x1234...',
            'recipient' => '0x5678...',
            'amount' => 10.0,
            'shardId' => 0,
            'gasPrice' => 1.5,
            'gasLimit' => 21000
        ])
    ]);

    // Initiate the transfer
    $transfer = $client->initiateCrossShardTransfer($transferRequest);
    echo "Cross-shard transfer initiated: {$transfer->transferId}\n";
    echo "Status: {$transfer->status}\n";

    // Monitor transfer status
    while (!in_array($transfer->status, ['completed', 'failed'])) {
        sleep(5); // Wait 5 seconds

        // Get latest blocks from both shards
        $sourceBlock = $client->getLatestBlock($transfer->fromShard);
        $targetBlock = $client->getLatestBlock($transfer->toShard);

        echo "Source shard block: {$sourceBlock->number}\n";
        echo "Target shard block: {$targetBlock->number}\n";

        // Check transaction inclusion
        foreach ([$sourceBlock, $targetBlock] as $block) {
            foreach ($block->transactions as $tx) {
                if ($tx->hash === $transfer->transaction->hash) {
                    echo "Transaction found in block {$block->number} of shard {$block->shardId}\n";
                    echo "Transaction status: {$tx->status}\n";
                }
            }
        }
    }
} catch (Exception $e) {
    echo "Error: {$e->getMessage()}\n";
} finally {
    $client->disconnect();
} 