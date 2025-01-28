use chrono::{DateTime, Utc};
use reqwest::{Client, header};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use anyhow::{Result, anyhow};

#[derive(Debug, Serialize, Deserialize)]
pub struct Transaction {
    pub hash: String,
    #[serde(rename = "from_address")]
    pub from_address: String,
    #[serde(rename = "to_address")]
    pub to_address: String,
    pub value: f64,
    pub timestamp: DateTime<Utc>,
    pub status: String,
    #[serde(rename = "block_number")]
    pub block_number: Option<u64>,
    #[serde(rename = "gas_used")]
    pub gas_used: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Block {
    pub number: u64,
    pub hash: String,
    pub timestamp: DateTime<Utc>,
    pub transactions: Vec<String>,
    pub validator: String,
    pub size: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Contract {
    pub address: String,
    pub creator: String,
    #[serde(rename = "creation_tx")]
    pub creation_tx: String,
    pub bytecode: String,
    pub abi: serde_json::Value,
}

pub struct VernachainSDK {
    client: Client,
    api_url: String,
}

impl VernachainSDK {
    pub fn new(api_url: &str, api_key: &str) -> Result<Self> {
        let mut headers = header::HeaderMap::new();
        headers.insert(
            "X-API-Key",
            header::HeaderValue::from_str(api_key)?
        );
        headers.insert(
            header::CONTENT_TYPE,
            header::HeaderValue::from_static("application/json")
        );

        let client = Client::builder()
            .default_headers(headers)
            .build()?;

        Ok(Self {
            client,
            api_url: api_url.trim_end_matches('/').to_string(),
        })
    }

    pub async fn get_block(&self, block_id: u64) -> Result<Block> {
        let response = self.client
            .get(&format!("{}/api/v1/block/{}", self.api_url, block_id))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        Ok(response.json().await?)
    }

    pub async fn get_transaction(&self, tx_hash: &str) -> Result<Transaction> {
        let response = self.client
            .get(&format!("{}/api/v1/transaction/{}", self.api_url, tx_hash))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        Ok(response.json().await?)
    }

    pub async fn get_balance(&self, address: &str) -> Result<f64> {
        let response = self.client
            .get(&format!("{}/api/v1/address/{}", self.api_url, address))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        let data: serde_json::Value = response.json().await?;
        Ok(data["balance"].as_f64().unwrap_or(0.0))
    }

    pub async fn send_transaction(
        &self,
        to_address: &str,
        value: f64,
        private_key: &str,
        gas_limit: Option<u64>,
        data: Option<&str>
    ) -> Result<String> {
        let payload = serde_json::json!({
            "to_address": to_address,
            "value": value,
            "private_key": private_key,
            "gas_limit": gas_limit,
            "data": data
        });

        let response = self.client
            .post(&format!("{}/api/v1/transaction", self.api_url))
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        let data: serde_json::Value = response.json().await?;
        Ok(data["transaction_hash"]
            .as_str()
            .ok_or_else(|| anyhow!("Invalid response format"))?
            .to_string())
    }

    pub async fn deploy_contract(
        &self,
        bytecode: &str,
        abi: &serde_json::Value,
        private_key: &str,
        constructor_args: Option<Vec<serde_json::Value>>,
        gas_limit: Option<u64>
    ) -> Result<String> {
        let payload = serde_json::json!({
            "bytecode": bytecode,
            "abi": abi,
            "private_key": private_key,
            "constructor_args": constructor_args,
            "gas_limit": gas_limit
        });

        let response = self.client
            .post(&format!("{}/api/v1/contract/deploy", self.api_url))
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        let data: serde_json::Value = response.json().await?;
        Ok(data["contract_address"]
            .as_str()
            .ok_or_else(|| anyhow!("Invalid response format"))?
            .to_string())
    }

    pub async fn call_contract(
        &self,
        contract_address: &str,
        function_name: &str,
        args: Vec<serde_json::Value>,
        abi: &serde_json::Value
    ) -> Result<serde_json::Value> {
        let payload = serde_json::json!({
            "contract_address": contract_address,
            "function_name": function_name,
            "args": args,
            "abi": abi
        });

        let response = self.client
            .post(&format!("{}/api/v1/contract/{}/call", self.api_url, contract_address))
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        let data: serde_json::Value = response.json().await?;
        Ok(data["result"].clone())
    }

    pub async fn bridge_transfer(
        &self,
        from_chain: &str,
        to_chain: &str,
        token: &str,
        amount: f64,
        to_address: &str,
        private_key: &str
    ) -> Result<String> {
        let payload = serde_json::json!({
            "from_chain": from_chain,
            "to_chain": to_chain,
            "token": token,
            "amount": amount,
            "to_address": to_address,
            "private_key": private_key
        });

        let response = self.client
            .post(&format!("{}/api/v1/bridge/transfer", self.api_url))
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        let data: serde_json::Value = response.json().await?;
        Ok(data["bridge_tx_hash"]
            .as_str()
            .ok_or_else(|| anyhow!("Invalid response format"))?
            .to_string())
    }

    pub async fn get_bridge_transaction(&self, tx_hash: &str) -> Result<serde_json::Value> {
        let response = self.client
            .get(&format!("{}/api/v1/bridge/transaction/{}", self.api_url, tx_hash))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        Ok(response.json().await?)
    }

    pub async fn get_network_stats(&self) -> Result<serde_json::Value> {
        let response = self.client
            .get(&format!("{}/api/v1/stats", self.api_url))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        Ok(response.json().await?)
    }

    pub async fn get_validators(&self) -> Result<Vec<serde_json::Value>> {
        let response = self.client
            .get(&format!("{}/api/v1/validators", self.api_url))
            .send()
            .await?;

        if !response.status().is_success() {
            let error = response.json::<serde_json::Value>().await?;
            return Err(anyhow!("API error: {}", error));
        }

        Ok(response.json().await?)
    }
} 