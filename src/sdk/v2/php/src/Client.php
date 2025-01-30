<?php

declare(strict_types=1);

namespace Vernachain\SDK;

use GuzzleHttp\Client as HttpClient;
use GuzzleHttp\Exception\GuzzleException;
use Ratchet\Client\WebSocket;
use Ratchet\Client\Connector as WebSocketClient;
use Vernachain\SDK\Types\{
    Transaction,
    Block,
    SmartContract,
    Validator,
    CrossShardTransfer,
    BridgeTransfer
};
use Vernachain\SDK\Exception\{
    VernachainException,
    ValidationException,
    NetworkException,
    AuthenticationException
};
use Psr\Log\LoggerInterface;
use React\EventLoop\Loop;

class Client
{
    private HttpClient $httpClient;
    private string $wsBaseUrl;

    public function __construct(
        string $nodeUrl,
        private ?string $apiKey = null,
        private ?LoggerInterface $logger = null
    ) {
        $this->httpClient = new HttpClient([
            'base_uri' => rtrim($nodeUrl, '/'),
            'headers' => $apiKey ? ['Authorization' => "Bearer {$apiKey}"] : [],
        ]);
        $this->wsBaseUrl = str_replace(['http://', 'https://'], ['ws://', 'wss://'], rtrim($nodeUrl, '/'));
    }

    /**
     * Create a new transaction
     */
    public function createTransaction(
        string $sender,
        string $recipient,
        float $amount,
        int $shardId = 0
    ): Transaction {
        try {
            $response = $this->httpClient->post('/api/v1/transactions', [
                'json' => [
                    'sender' => $sender,
                    'recipient' => $recipient,
                    'amount' => $amount,
                    'shard_id' => $shardId,
                ],
            ]);

            return Transaction::fromArray(
                json_decode($response->getBody()->getContents(), true)
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Get transaction by hash
     */
    public function getTransaction(string $txHash): Transaction
    {
        try {
            $response = $this->httpClient->get("/api/v1/transactions/{$txHash}");
            return Transaction::fromArray(
                json_decode($response->getBody()->getContents(), true)
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Get block by number
     */
    public function getBlock(int $blockNumber, int $shardId = 0): Block
    {
        try {
            $response = $this->httpClient->get(
                "/api/v1/blocks/{$blockNumber}",
                ['query' => ['shard_id' => $shardId]]
            );
            return Block::fromArray(
                json_decode($response->getBody()->getContents(), true)
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Deploy a smart contract
     */
    public function deployContract(
        string $contractType,
        array $params,
        int $shardId = 0
    ): SmartContract {
        try {
            $response = $this->httpClient->post('/api/v1/contracts', [
                'json' => [
                    'contract_type' => $contractType,
                    'params' => $params,
                    'shard_id' => $shardId,
                ],
            ]);
            return SmartContract::fromArray(
                json_decode($response->getBody()->getContents(), true)
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Subscribe to new blocks
     */
    public function subscribeToBlocks(
        callable $onBlock,
        callable $onError,
        int $shardId = 0
    ): void {
        $loop = Loop::get();
        $connector = new WebSocketClient($loop);

        $connector("{$this->wsBaseUrl}/ws/blocks?shard_id={$shardId}")
            ->then(
                function (WebSocket $conn) use ($onBlock, $onError) {
                    $conn->on('message', function ($msg) use ($onBlock) {
                        try {
                            $block = Block::fromArray(json_decode($msg, true));
                            $onBlock($block);
                        } catch (\Exception $e) {
                            $this->logger?->error('Failed to parse block', [
                                'error' => $e->getMessage(),
                                'data' => $msg,
                            ]);
                        }
                    });

                    $conn->on('error', function ($error) use ($onError) {
                        $onError(new NetworkException(
                            "WebSocket error: {$error->getMessage()}"
                        ));
                    });
                },
                function (\Exception $e) use ($onError) {
                    $onError(new NetworkException(
                        "Failed to connect to WebSocket: {$e->getMessage()}"
                    ));
                }
            );

        $loop->run();
    }

    /**
     * Get validator set
     */
    public function getValidatorSet(int $shardId = 0): array
    {
        try {
            $response = $this->httpClient->get(
                '/api/v1/validators',
                ['query' => ['shard_id' => $shardId]]
            );
            $data = json_decode($response->getBody()->getContents(), true);
            return array_map(
                fn (array $v) => Validator::fromArray($v),
                $data['validators']
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Initiate bridge transfer
     */
    public function bridgeTransfer(
        string $targetChain,
        float $amount,
        string $recipient
    ): BridgeTransfer {
        try {
            $response = $this->httpClient->post('/api/v1/bridge/transfer', [
                'json' => [
                    'target_chain' => $targetChain,
                    'amount' => $amount,
                    'recipient' => $recipient,
                ],
            ]);
            return BridgeTransfer::fromArray(
                json_decode($response->getBody()->getContents(), true)
            );
        } catch (GuzzleException $e) {
            $this->handleHttpException($e);
        }
    }

    /**
     * Handle HTTP exceptions
     */
    private function handleHttpException(GuzzleException $e): never
    {
        $response = method_exists($e, 'getResponse') ? $e->getResponse() : null;
        $statusCode = $response?->getStatusCode();
        $body = $response ? json_decode($response->getBody()->getContents(), true) : null;
        $message = $body['message'] ?? $e->getMessage();

        $this->logger?->error('API request failed', [
            'status_code' => $statusCode,
            'message' => $message,
            'error' => $e->getMessage(),
        ]);

        throw match ($statusCode) {
            401 => new AuthenticationException('Invalid API key'),
            400 => new ValidationException($message),
            default => new NetworkException("API request failed: {$message}"),
        };
    }
}