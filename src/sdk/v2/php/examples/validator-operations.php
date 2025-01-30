<?php

require_once __DIR__ . '/../vendor/autoload.php';

use Vernachain\SDK\Client;

$client = new Client([
    'nodeUrl' => 'http://localhost:8545',
    'apiKey' => 'your-api-key'
]);

try {
    // Get validator set for shard 0
    $validators = $client->getValidatorSet(0);
    echo "Found " . count($validators) . " validators in shard 0\n";

    // Print validator details
    foreach ($validators as $validator) {
        echo "\nValidator: {$validator->address}\n";
        echo "Stake: {$validator->stake} VRN\n";
        echo "Reputation: {$validator->reputation}\n";
        echo "Active: " . ($validator->isActive ? 'Yes' : 'No') . "\n";
        echo "Commission Rate: " . ($validator->commissionRate ?? 0.0) . "%\n";

        if ($validator->delegators) {
            echo "Delegators: " . count($validator->delegators) . "\n";
            $totalDelegated = array_reduce(
                $validator->delegators,
                fn($sum, $d) => $sum + ($d['amount'] ?? 0),
                0
            );
            echo "Total Delegated: {$totalDelegated} VRN\n";
        }
    }

    // Find the validator with highest reputation
    $bestValidator = array_reduce(
        $validators,
        fn($best, $current) => $current->reputation > $best->reputation ? $current : $best,
        $validators[0]
    );
    echo "\nBest validator by reputation: {$bestValidator->address}\n";

    // Stake tokens on the best validator
    $stakeAmount = 100.0; // VRN tokens
    $stakeResult = $client->stake($stakeAmount, $bestValidator->address);
    echo "\nStaked {$stakeAmount} VRN on validator {$bestValidator->address}\n";
    echo "Transaction hash: {$stakeResult['transactionHash']}\n";

    // Monitor validator performance
    echo "\nMonitoring validator performance...\n";
    for ($i = 0; $i < 3; $i++) {
        sleep(10); // Wait 10 seconds

        $updatedValidators = $client->getValidatorSet(0);
        $updatedValidator = array_values(array_filter(
            $updatedValidators,
            fn($v) => $v->address === $bestValidator->address
        ))[0] ?? null;

        if ($updatedValidator) {
            echo "\nValidator {$updatedValidator->address} status:\n";
            echo "Total Blocks Validated: {$updatedValidator->totalBlocksValidated}\n";
            echo "Current Reputation: {$updatedValidator->reputation}\n";
            echo "Total Stake: {$updatedValidator->stake} VRN\n";
        }
    }
} catch (Exception $e) {
    echo "Error: {$e->getMessage()}\n";
} finally {
    $client->disconnect();
} 