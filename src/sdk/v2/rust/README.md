# Vernachain Rust SDK v2

A comprehensive Rust SDK for interacting with the Vernachain blockchain platform.

## Features

- Async/await support with Tokio
- Strong type safety with Serde
- WebSocket subscriptions using tokio-tungstenite
- Comprehensive error handling with thiserror
- Cross-shard transaction support
- Smart contract interactions
- Bridge operations

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
vernachain-sdk = "2.0.0"
tokio = { version = "1.34.0", features = ["full"] }
```

## Quick Start

```rust
use vernachain_sdk::prelude::*;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize client
    let client = VernachainClient::new(
        "http://node-url",
        Some("your-api-key".to_string())
    );
    
    // Create transaction
    let tx = client.create_transaction(TransactionRequest {
        sender: "0x...".to_string(),
        recipient: "0x...".to_string(),
        amount: 1.0,
        shard_id: 0,
        ..Default::default()
    }).await?;
    
    // Get block
    let block = client.get_latest_block(0).await?;
    
    // Deploy smart contract
    let contract = client.deploy_contract(ContractDeployRequest {
        contract_type: "ERC20".to_string(),
        params: serde_json::json!({
            "name": "MyToken",
            "symbol": "MTK"
        }),
        shard_id: 0,
        ..Default::default()
    }).await?;
    
    // Subscribe to new blocks
    let mut block_rx = client.subscribe_blocks(0).await?;
    while let Ok(block) = block_rx.recv().await {
        println!("New block: {}", block.number);
    }

    Ok(())
}
```

## API Reference

### Transaction Methods
- `create_transaction(request: TransactionRequest) -> Result<Transaction>`
- `get_transaction(tx_hash: &str) -> Result<Transaction>`

### Block Methods
- `get_block(block_number: u64, shard_id: u64) -> Result<Block>`
- `get_latest_block(shard_id: u64) -> Result<Block>`

### Smart Contract Methods
- `deploy_contract(request: ContractDeployRequest) -> Result<SmartContract>`
- `call_contract(address: &str, method: &str, params: Value) -> Result<Value>`

### Cross-Shard Operations
- `initiate_cross_shard_transfer(request: CrossShardTransferRequest) -> Result<CrossShardTransfer>`

### WebSocket Subscriptions
- `subscribe_blocks(shard_id: u64) -> Result<Receiver<Block>>`

### Validator Operations
- `get_validator_set(shard_id: u64) -> Result<Vec<Validator>>`
- `stake(amount: f64, validator_address: &str) -> Result<Value>`

### Bridge Operations
- `bridge_transfer(request: BridgeTransferRequest) -> Result<BridgeTransfer>`

## Error Handling

The SDK uses the `thiserror` crate for error handling:

```rust
use vernachain_sdk::VernachainError;

match client.get_transaction("0x...").await {
    Ok(tx) => println!("Transaction: {:?}", tx),
    Err(VernachainError::AuthenticationError) => eprintln!("Invalid API key"),
    Err(VernachainError::NetworkError(e)) => eprintln!("Network error: {}", e),
    Err(e) => eprintln!("Other error: {}", e),
}
```

## WebSocket Subscriptions

The SDK uses Tokio's broadcast channel for WebSocket subscriptions:

```rust
let mut block_rx = client.subscribe_blocks(0).await?;
tokio::spawn(async move {
    while let Ok(block) = block_rx.recv().await {
        println!("New block: {:?}", block);
    }
});
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 