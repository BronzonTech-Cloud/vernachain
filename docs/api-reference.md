# Vernachain API Reference

This document provides detailed information about the Vernachain API endpoints, request/response formats, and authentication methods.

## Table of Contents
- [Authentication](#authentication)
- [Base URLs](#base-urls)
- [Node API](#node-api)
- [Blockchain API](#blockchain-api)
- [Wallet API](#wallet-api)
- [Smart Contract API](#smart-contract-api)
- [Bridge API](#bridge-api)
- [WebSocket Events](#websocket-events)

## Authentication

All API requests require an API key to be included in the header:
```http
X-API-Key: your_api_key_here
```

Rate limits:
- 100 requests per minute for regular endpoints
- 30 requests per minute for heavy operations

### Endpoints

#### POST /api/v1/auth/register
Register a new user.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password",
    "confirm_password": "password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registration successful"
}
```

#### POST /api/v1/auth/login
Login with credentials.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "token": "jwt_token_here"
    }
}
```

## Base URLs

- Node API: `http://localhost:8000/api/v1`
- Explorer API: `http://localhost:8001/api/v1`
- WebSocket: `ws://localhost:8000/ws`

## Node API

### Get Node Status
```http
GET /node/status
```

Response:
```json
{
  "node_id": "string",
  "version": "string",
  "peers_count": 0,
  "is_syncing": false,
  "latest_block": 0,
  "uptime": 0
}
```

### Get Peers List
```http
GET /node/peers
```

Response:
```json
{
  "peers": [
    {
      "node_id": "string",
      "address": "string",
      "port": 0,
      "last_seen": "timestamp"
    }
  ]
}
```

## Blockchain API

### Transaction Operations

#### Create Transaction
```http
POST /api/v1/transactions
```

Request body:
```json
{
    "from_address": "string",
    "to_address": "string",
    "amount": "number",
    "nonce": "number",
    "signature": "string"
}
```

#### Get Transaction
```http
GET /api/v1/transactions/{transaction_hash}
```

Response:
```json
{
    "hash": "string",
    "from_address": "string",
    "to_address": "string",
    "amount": "number",
    "nonce": "number",
    "signature": "string",
    "status": "string",
    "block_number": "number",
    "timestamp": "number"
}
```

### Block Operations

#### Get Block
```http
GET /api/v1/blocks/{block_number}
```

Response:
```json
{
    "index": "number",
    "hash": "string",
    "previous_hash": "string",
    "timestamp": "number",
    "transactions": "array",
    "validator": "string",
    "merkle_root": "string"
}
```

### Shard Operations

#### Get Shard Info
```http
GET /api/v1/shards/{shard_id}
```

Response:
```json
{
    "shard_id": "number",
    "validator_set": "array",
    "state_root": "string",
    "last_block_height": "number",
    "pending_messages": "number",
    "processed_messages": "number"
}
```

### Cross-Shard Operations

#### Create Cross-Shard Transaction
```http
POST /api/v1/cross-shard/transactions
```

Request body:
```json
{
    "from_shard": "number",
    "to_shard": "number",
    "transaction": {
        "from_address": "string",
        "to_address": "string",
        "amount": "number",
        "nonce": "number",
        "signature": "string"
    }
}
```

### Validator Operations

#### Get Validator Info
```http
GET /api/v1/validators/{address}
```

Response:
```json
{
    "address": "string",
    "stake": "number",
    "is_active": "boolean",
    "reputation_score": "number",
    "blocks_produced": "number"
}
```

## Wallet API

### Get Balance
```http
GET /wallets/{address}/balance
```

Response:
```json
{
  "address": "string",
  "balance": "number",
  "staked": "number",
  "nonce": 0
}
```

### Get Transaction History
```http
GET /wallets/{address}/transactions
```

Parameters:
- `limit` (optional): Number of transactions to return
- `offset` (optional): Pagination offset
- `status` (optional): Transaction status filter

## Smart Contract API

### Deploy Contract
```http
POST /contracts/deploy
```

Request:
```json
{
  "bytecode": "string",
  "abi": "string",
  "constructor_args": "string",
  "sender": "string",
  "signature": "string"
}
```

### Call Contract
```http
POST /contracts/{address}/call
```

Request:
```json
{
  "function": "string",
  "args": "string",
  "sender": "string",
  "signature": "string"
}
```

### Get Contract
```http
GET /contracts/{address}
```

Response:
```json
{
  "address": "string",
  "creator": "string",
  "created_at": "timestamp",
  "abi": "string",
  "bytecode": "string"
}
```

## Bridge API

### Initiate Transfer
```http
POST /bridge/transfer
```

Request:
```json
{
  "from_chain": "string",
  "to_chain": "string",
  "token": "string",
  "amount": "number",
  "recipient": "string",
  "signature": "string"
}
```

### Get Transfer Status
```http
GET /bridge/transfers/{tx_hash}
```

Response:
```json
{
  "hash": "string",
  "status": "string",
  "from_chain": "string",
  "to_chain": "string",
  "amount": "number",
  "timestamp": "timestamp"
}
```

## WebSocket Events

Connect to WebSocket endpoint:
```javascript
ws://localhost:8000/ws
```

### Subscribe to Events
```json
{
  "type": "subscribe",
  "channels": [
    "blocks",
    "transactions",
    "validators"
  ]
}
```

### Event Types

1. New Block Event:
```json
{
  "type": "block",
  "data": {
    "index": 0,
    "hash": "string",
    "transactions": []
  }
}
```

2. New Transaction Event:
```json
{
  "type": "transaction",
  "data": {
    "hash": "string",
    "from": "string",
    "to": "string",
    "value": "number"
  }
}
```

3. Validator Event:
```json
{
  "type": "validator",
  "data": {
    "address": "string",
    "action": "string",
    "stake": "number"
  }
}
```

## Error Handling

All API errors follow this format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Common Error Codes:
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## Pagination

For endpoints that return lists, use these query parameters:
- `limit`: Number of items per page (default: 10, max: 100)
- `offset`: Number of items to skip (default: 0)
- `order`: Sort order (asc/desc)

Response format includes pagination metadata:
```json
{
  "data": [],
  "pagination": {
    "total": 0,
    "limit": 0,
    "offset": 0,
    "has_more": false
  }
}
```

## Rate Limiting

Response headers include rate limit information:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1635724800
```

## Explorer API

### Network Statistics

#### GET /stats
Get detailed network statistics.

**Response:**
```json
{
    "total_blocks": 1000,
    "total_transactions": 5000,
    "total_addresses": 200,
    "total_validators": 10,
    "total_shards": 4,
    "average_block_time": 5.0,
    "current_tps": 100,
    "peak_tps": 150,
    "total_staked": 1000000,
    "current_difficulty": 12345,
    "hash_rate": 1000000
}
```

### Blocks

#### GET /blocks
Get paginated list of blocks.

**Parameters:**
- page (int): Page number
- limit (int): Items per page
- include_transactions (bool): Include full transaction details

### Transactions

#### GET /transactions
Get paginated list of transactions.

**Parameters:**
- page (int): Page number
- limit (int): Items per page
- address (string): Filter by address
- type (string): Filter by transaction type
- status (string): Filter by status

### Validators

#### GET /validators
Get list of validators with detailed information.

**Response:**
```json
[
    {
        "address": "0x...",
        "total_stake": 100000,
        "self_stake": 50000,
        "delegators": 10,
        "blocks_validated": 100,
        "uptime": 99.9,
        "commission_rate": 0.05,
        "rewards_earned": 1000,
        "performance_score": 95.5,
        "status": "active"
    }
]
```

## WebSocket API

### Channels
- stats: Network statistics updates
- blocks: New block notifications
- transactions: New transaction notifications
- validators: Validator status updates

### Connection
```javascript
ws://your-node:port/ws/{channel}
```

### Real-time Block Updates
```websocket
ws://api/v1/ws/blocks
```

Message format:
```json
{
    "type": "new_block",
    "data": {
        "index": "number",
        "hash": "string",
        "previous_hash": "string",
        "timestamp": "number",
        "transactions": "array",
        "validator": "string"
    }
}
```

### Real-time Transaction Updates
```websocket
ws://api/v1/ws/transactions
```

Message format:
```json
{
    "type": "new_transaction",
    "data": {
        "hash": "string",
        "from_address": "string",
        "to_address": "string",
        "amount": "number",
        "status": "string"
    }
}
```

## Security

All API endpoints are protected with:
- Rate limiting
- JWT authentication
- CORS protection
- Input validation