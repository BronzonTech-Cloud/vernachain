<?php

/**
 * Vernachain PHP SDK.
 * 
 * This module provides a PHP interface for interacting with the Vernachain blockchain.
 */

namespace Vernachain;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class Transaction {
    public string $hash;
    public string $fromAddress;
    public string $toAddress;
    public float $value;
    public \DateTime $timestamp;
    public string $status;
    public ?int $blockNumber;
    public ?int $gasUsed;

    public function __construct(array $data) {
        $this->hash = $data['hash'];
        $this->fromAddress = $data['from_address'];
        $this->toAddress = $data['to_address'];
        $this->value = $data['value'];
        $this->timestamp = new \DateTime($data['timestamp']);
        $this->status = $data['status'];
        $this->blockNumber = $data['block_number'] ?? null;
        $this->gasUsed = $data['gas_used'] ?? null;
    }
}

class Block {
    public int $number;
    public string $hash;
    public \DateTime $timestamp;
    public array $transactions;
    public string $validator;
    public int $size;

    public function __construct(array $data) {
        $this->number = $data['number'];
        $this->hash = $data['hash'];
        $this->timestamp = new \DateTime($data['timestamp']);
        $this->transactions = $data['transactions'];
        $this->validator = $data['validator'];
        $this->size = $data['size'];
    }
}

class Contract {
    public string $address;
    public string $creator;
    public string $creationTx;
    public string $bytecode;
    public array $abi;

    public function __construct(array $data) {
        $this->address = $data['address'];
        $this->creator = $data['creator'];
        $this->creationTx = $data['creation_tx'];
        $this->bytecode = $data['bytecode'];
        $this->abi = $data['abi'];
    }
}

class VernachainSDK {
    private Client $client;
    private string $apiUrl;
    private array $headers;

    /**
     * Initialize the SDK.
     * 
     * @param string $apiUrl Base URL for the API
     * @param string $apiKey API key for authentication
     */
    public function __construct(string $apiUrl, string $apiKey) {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->headers = [
            'X-API-Key' => $apiKey,
            'Content-Type' => 'application/json'
        ];
        $this->client = new Client([
            'headers' => $this->headers,
            'http_errors' => true
        ]);
    }

    /**
     * Get block details by ID.
     * 
     * @param int $blockId Block number
     * @return Block
     * @throws GuzzleException
     */
    public function getBlock(int $blockId): Block {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/block/{$blockId}"
        );
        $data = json_decode($response->getBody(), true);
        return new Block($data);
    }

    /**
     * Get transaction details by hash.
     * 
     * @param string $txHash Transaction hash
     * @return Transaction
     * @throws GuzzleException
     */
    public function getTransaction(string $txHash): Transaction {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/transaction/{$txHash}"
        );
        $data = json_decode($response->getBody(), true);
        return new Transaction($data);
    }

    /**
     * Get address balance.
     * 
     * @param string $address Wallet address
     * @return float
     * @throws GuzzleException
     */
    public function getBalance(string $address): float {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/address/{$address}"
        );
        $data = json_decode($response->getBody(), true);
        return (float) $data['balance'];
    }

    /**
     * Send a transaction.
     * 
     * @param string $toAddress Recipient address
     * @param float $value Amount to send
     * @param string $privateKey Sender's private key
     * @param int|null $gasLimit Optional gas limit
     * @param string|null $data Optional contract data
     * @return string Transaction hash
     * @throws GuzzleException
     */
    public function sendTransaction(
        string $toAddress,
        float $value,
        string $privateKey,
        ?int $gasLimit = null,
        ?string $data = null
    ): string {
        $payload = [
            'to_address' => $toAddress,
            'value' => $value,
            'private_key' => $privateKey,
            'gas_limit' => $gasLimit,
            'data' => $data
        ];

        $response = $this->client->post(
            "{$this->apiUrl}/api/v1/transaction",
            ['json' => $payload]
        );
        $data = json_decode($response->getBody(), true);
        return $data['transaction_hash'];
    }

    /**
     * Deploy a smart contract.
     * 
     * @param string $bytecode Contract bytecode
     * @param array $abi Contract ABI
     * @param string $privateKey Deployer's private key
     * @param array|null $constructorArgs Constructor arguments
     * @param int|null $gasLimit Optional gas limit
     * @return string Contract address
     * @throws GuzzleException
     */
    public function deployContract(
        string $bytecode,
        array $abi,
        string $privateKey,
        ?array $constructorArgs = null,
        ?int $gasLimit = null
    ): string {
        $payload = [
            'bytecode' => $bytecode,
            'abi' => $abi,
            'private_key' => $privateKey,
            'constructor_args' => $constructorArgs,
            'gas_limit' => $gasLimit
        ];

        $response = $this->client->post(
            "{$this->apiUrl}/api/v1/contract/deploy",
            ['json' => $payload]
        );
        $data = json_decode($response->getBody(), true);
        return $data['contract_address'];
    }

    /**
     * Call a contract function.
     * 
     * @param string $contractAddress Contract address
     * @param string $functionName Function to call
     * @param array $args Function arguments
     * @param array $abi Contract ABI
     * @return mixed Function result
     * @throws GuzzleException
     */
    public function callContract(
        string $contractAddress,
        string $functionName,
        array $args,
        array $abi
    ) {
        $payload = [
            'contract_address' => $contractAddress,
            'function_name' => $functionName,
            'args' => $args,
            'abi' => $abi
        ];

        $response = $this->client->post(
            "{$this->apiUrl}/api/v1/contract/{$contractAddress}/call",
            ['json' => $payload]
        );
        $data = json_decode($response->getBody(), true);
        return $data['result'];
    }

    /**
     * Initiate a cross-chain transfer.
     * 
     * @param string $fromChain Source chain
     * @param string $toChain Target chain
     * @param string $token Token symbol
     * @param float $amount Amount to transfer
     * @param string $toAddress Recipient address
     * @param string $privateKey Sender's private key
     * @return string Bridge transaction hash
     * @throws GuzzleException
     */
    public function bridgeTransfer(
        string $fromChain,
        string $toChain,
        string $token,
        float $amount,
        string $toAddress,
        string $privateKey
    ): string {
        $payload = [
            'from_chain' => $fromChain,
            'to_chain' => $toChain,
            'token' => $token,
            'amount' => $amount,
            'to_address' => $toAddress,
            'private_key' => $privateKey
        ];

        $response = $this->client->post(
            "{$this->apiUrl}/api/v1/bridge/transfer",
            ['json' => $payload]
        );
        $data = json_decode($response->getBody(), true);
        return $data['bridge_tx_hash'];
    }

    /**
     * Get bridge transaction status.
     * 
     * @param string $txHash Bridge transaction hash
     * @return array
     * @throws GuzzleException
     */
    public function getBridgeTransaction(string $txHash): array {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/bridge/transaction/{$txHash}"
        );
        return json_decode($response->getBody(), true);
    }

    /**
     * Get network statistics.
     * 
     * @return array
     * @throws GuzzleException
     */
    public function getNetworkStats(): array {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/stats"
        );
        return json_decode($response->getBody(), true);
    }

    /**
     * Get list of validators and their stats.
     * 
     * @return array
     * @throws GuzzleException
     */
    public function getValidators(): array {
        $response = $this->client->get(
            "{$this->apiUrl}/api/v1/validators"
        );
        return json_decode($response->getBody(), true);
    }
} 