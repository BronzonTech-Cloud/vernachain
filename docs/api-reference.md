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

### Get Block
```http
GET /blocks/{block_id}
```

Response:
```json
{
  "index": 0,
  "hash": "string",
  "previous_hash": "string",
  "timestamp": "timestamp",
  "transactions": [],
  "validator": "string",
  "signature": "string"
}
```

### Get Transaction
```http
GET /transactions/{tx_hash}
```

Response:
```json
{
  "hash": "string",
  "from": "string",
  "to": "string",
  "value": "number",
  "timestamp": "timestamp",
  "block_hash": "string",
  "status": "string"
}
```

### Send Transaction
```http
POST /transactions
```

Request:
```json
{
  "from": "string",
  "to": "string",
  "value": "number",
  "data": "string",
  "signature": "string"
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