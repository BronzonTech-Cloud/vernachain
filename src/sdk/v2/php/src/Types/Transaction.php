<?php

declare(strict_types=1);

namespace Vernachain\SDK\Types;

use DateTimeImmutable;
use Symfony\Component\Validator\Constraints as Assert;

class Transaction
{
    public function __construct(
        #[Assert\NotBlank]
        public readonly string $hash,

        #[Assert\NotBlank]
        public readonly string $sender,

        #[Assert\NotBlank]
        public readonly string $recipient,

        #[Assert\PositiveOrZero]
        public readonly float $amount,

        #[Assert\NotNull]
        public readonly DateTimeImmutable $timestamp,

        #[Assert\PositiveOrZero]
        public readonly int $shard_id,

        #[Assert\NotBlank]
        public readonly string $status,

        public readonly ?string $signature = null,
        public readonly ?int $nonce = null,
        public readonly ?float $gas_price = null,
        public readonly ?int $gas_limit = null,
        public readonly ?array $data = null
    ) {}

    public static function fromArray(array $data): self
    {
        return new self(
            hash: $data['hash'],
            sender: $data['sender'],
            recipient: $data['recipient'],
            amount: $data['amount'],
            timestamp: new DateTimeImmutable($data['timestamp']),
            shard_id: $data['shard_id'],
            status: $data['status'],
            signature: $data['signature'] ?? null,
            nonce: $data['nonce'] ?? null,
            gas_price: $data['gas_price'] ?? null,
            gas_limit: $data['gas_limit'] ?? null,
            data: $data['data'] ?? null
        );
    }

    public function toArray(): array
    {
        return [
            'hash' => $this->hash,
            'sender' => $this->sender,
            'recipient' => $this->recipient,
            'amount' => $this->amount,
            'timestamp' => $this->timestamp->format(DATE_ATOM),
            'shard_id' => $this->shard_id,
            'status' => $this->status,
            'signature' => $this->signature,
            'nonce' => $this->nonce,
            'gas_price' => $this->gas_price,
            'gas_limit' => $this->gas_limit,
            'data' => $this->data,
        ];
    }
} 