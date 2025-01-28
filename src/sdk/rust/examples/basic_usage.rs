use vernachain_sdk::VernachainSDK;
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize the SDK with API URL and key
    let sdk = VernachainSDK::new(
        "https://api.vernachain.com",
        "your-api-key-here"
    )?;

    // Get network stats
    let stats = sdk.get_network_stats().await?;
    println!("Network Stats: {:?}", stats);

    // Get latest validators
    let validators = sdk.get_validators().await?;
    println!("Active Validators: {:?}", validators);

    // Get balance of an address
    let address = "0x1234567890abcdef1234567890abcdef12345678";
    let balance = sdk.get_balance(address).await?;
    println!("Balance of {}: {} VERNA", address, balance);

    // Send a transaction
    let tx_hash = sdk.send_transaction(
        "0xrecipient_address",
        1.5, // amount
        "your-private-key",
        Some(21000), // gas limit
        None, // no contract data
    ).await?;
    println!("Transaction sent: {}", tx_hash);

    // Get transaction details
    let tx = sdk.get_transaction(&tx_hash).await?;
    println!("Transaction details: {:?}", tx);

    // Deploy a smart contract
    let contract_address = sdk.deploy_contract(
        "0x608060405234801561001057600080fd5b50610150806100206000396000f3",
        &serde_json::json!([/* ABI here */]),
        "your-private-key",
        None, // no constructor args
        Some(500000), // gas limit
    ).await?;
    println!("Contract deployed at: {}", contract_address);

    // Call a contract function
    let result = sdk.call_contract(
        &contract_address,
        "balanceOf",
        vec![serde_json::json!(address)],
        &serde_json::json!([/* ABI here */]),
    ).await?;
    println!("Contract call result: {:?}", result);

    // Initiate a cross-chain transfer
    let bridge_tx = sdk.bridge_transfer(
        "vernachain",
        "ethereum",
        "VERNA",
        0.5,
        "0xeth_recipient_address",
        "your-private-key",
    ).await?;
    println!("Bridge transfer initiated: {}", bridge_tx);

    // Get bridge transaction status
    let bridge_status = sdk.get_bridge_transaction(&bridge_tx).await?;
    println!("Bridge transaction status: {:?}", bridge_status);

    Ok(())
} 