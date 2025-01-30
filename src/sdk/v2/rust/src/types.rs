use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub hash: String,
    pub sender: String,
    pub recipient: String,
    pub amount: f64,
    pub timestamp: DateTime<Utc>,
    pub shard_id: u64,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signature: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub nonce: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_price: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_limit: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub number: u64,
    pub hash: String,
    pub previous_hash: String,
    pub timestamp: DateTime<Utc>,
    pub transactions: Vec<Transaction>,
    pub validator: String,
    pub shard_id: u64,
    pub merkle_root: String,
    pub state_root: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signature: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub size: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_used: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_limit: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SmartContract {
    pub address: String,
    pub contract_type: String,
    pub creator: String,
    pub creation_timestamp: DateTime<Utc>,
    pub shard_id: u64,
    pub abi: HashMap<String, serde_json::Value>,
    pub bytecode: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub state: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Validator {
    pub address: String,
    pub stake: f64,
    pub reputation: f64,
    pub total_blocks_validated: u64,
    pub is_active: bool,
    pub last_active: DateTime<Utc>,
    pub shard_id: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub commission_rate: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub delegators: Option<Vec<HashMap<String, serde_json::Value>>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrossShardTransfer {
    pub transfer_id: String,
    pub from_shard: u64,
    pub to_shard: u64,
    pub transaction: Transaction,
    pub status: String,
    pub initiated_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub completed_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub proof: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeTransfer {
    pub transfer_id: String,
    pub source_chain: String,
    pub target_chain: String,
    pub amount: f64,
    pub sender: String,
    pub recipient: String,
    pub status: String,
    pub initiated_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub completed_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub proof: Option<HashMap<String, serde_json::Value>>,
}

// Request types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransactionRequest {
    pub sender: String,
    pub recipient: String,
    pub amount: f64,
    #[serde(default)]
    pub shard_id: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_price: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_limit: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractDeployRequest {
    pub contract_type: String,
    pub params: HashMap<String, serde_json::Value>,
    #[serde(default)]
    pub shard_id: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_limit: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrossShardTransferRequest {
    pub from_shard: u64,
    pub to_shard: u64,
    pub transaction: TransactionRequest,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeTransferRequest {
    pub target_chain: String,
    pub amount: f64,
    pub recipient: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_limit: Option<u64>,
} 