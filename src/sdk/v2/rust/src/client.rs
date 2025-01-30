use crate::{
    error::{Result, VernachainError},
    types::*,
};
use futures_util::{SinkExt, StreamExt};
use reqwest::{header::{HeaderMap, HeaderValue}, Client as HttpClient};
use serde::de::DeserializeOwned;
use serde_json::json;
use std::sync::Arc;
use tokio::sync::broadcast;
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use tracing::{debug, error, info};
use url::Url;

#[derive(Clone)]
pub struct VernachainClient {
    http_client: HttpClient,
    base_url: String,
    ws_url: String,
    api_key: Option<String>,
}

impl VernachainClient {
    pub fn new(node_url: &str, api_key: Option<String>) -> Self {
        let mut headers = HeaderMap::new();
        if let Some(key) = &api_key {
            headers.insert(
                "Authorization",
                HeaderValue::from_str(&format!("Bearer {}", key)).unwrap(),
            );
        }

        let http_client = HttpClient::builder()
            .default_headers(headers)
            .build()
            .expect("Failed to create HTTP client");

        let ws_url = node_url.replace("http", "ws");

        Self {
            http_client,
            base_url: node_url.trim_end_matches('/').to_string(),
            ws_url,
            api_key,
        }
    }

    async fn request<T>(&self, method: &str, endpoint: &str, body: Option<serde_json::Value>) -> Result<T>
    where
        T: DeserializeOwned,
    {
        let url = format!("{}{}", self.base_url, endpoint);
        let mut request = self.http_client.request(
            method.parse().map_err(|_| VernachainError::InternalError("Invalid HTTP method".into()))?,
            &url,
        );

        if let Some(data) = body {
            request = request.json(&data);
        }

        let response = request.send().await?;
        
        if !response.status().is_success() {
            match response.status().as_u16() {
                401 => return Err(VernachainError::AuthenticationError),
                429 => return Err(VernachainError::RateLimitError),
                _ => {
                    let error_text = response.text().await?;
                    return Err(VernachainError::NetworkError(error_text));
                }
            }
        }

        let data = response.json().await?;
        Ok(data)
    }

    // Transaction Methods
    pub async fn create_transaction(&self, request: TransactionRequest) -> Result<Transaction> {
        self.request(
            "POST",
            "/api/v1/transactions",
            Some(serde_json::to_value(request)?),
        )
        .await
    }

    pub async fn get_transaction(&self, tx_hash: &str) -> Result<Transaction> {
        self.request("GET", &format!("/api/v1/transactions/{}", tx_hash), None).await
    }

    // Block Methods
    pub async fn get_block(&self, block_number: u64, shard_id: u64) -> Result<Block> {
        self.request(
            "GET",
            &format!("/api/v1/blocks/{}?shard_id={}", block_number, shard_id),
            None,
        )
        .await
    }

    pub async fn get_latest_block(&self, shard_id: u64) -> Result<Block> {
        self.request(
            "GET",
            &format!("/api/v1/blocks/latest?shard_id={}", shard_id),
            None,
        )
        .await
    }

    // Smart Contract Methods
    pub async fn deploy_contract(&self, request: ContractDeployRequest) -> Result<SmartContract> {
        self.request(
            "POST",
            "/api/v1/contracts",
            Some(serde_json::to_value(request)?),
        )
        .await
    }

    pub async fn call_contract(
        &self,
        contract_address: &str,
        method: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value> {
        self.request(
            "POST",
            &format!("/api/v1/contracts/{}/call", contract_address),
            Some(json!({
                "method": method,
                "params": params,
            })),
        )
        .await
    }

    // Cross-Shard Operations
    pub async fn initiate_cross_shard_transfer(
        &self,
        request: CrossShardTransferRequest,
    ) -> Result<CrossShardTransfer> {
        self.request(
            "POST",
            "/api/v1/cross-shard/transfer",
            Some(serde_json::to_value(request)?),
        )
        .await
    }

    // WebSocket Subscriptions
    pub async fn subscribe_blocks(
        &self,
        shard_id: u64,
    ) -> Result<broadcast::Receiver<Block>> {
        let (tx, rx) = broadcast::channel(100);
        let ws_url = format!("{}/ws/blocks?shard_id={}", self.ws_url, shard_id);
        let tx = Arc::new(tx);

        let url = Url::parse(&ws_url).map_err(|e| VernachainError::InternalError(e.to_string()))?;
        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();

        // Handle API key authentication if needed
        if let Some(key) = &self.api_key {
            write
                .send(Message::Text(json!({ "type": "auth", "token": key }).to_string()))
                .await?;
        }

        let tx_clone = tx.clone();
        tokio::spawn(async move {
            while let Some(msg) = read.next().await {
                match msg {
                    Ok(Message::Text(text)) => {
                        match serde_json::from_str::<Block>(&text) {
                            Ok(block) => {
                                if tx_clone.send(block).is_err() {
                                    break;
                                }
                            }
                            Err(e) => error!("Failed to parse block data: {}", e),
                        }
                    }
                    Ok(Message::Close(_)) => break,
                    Err(e) => {
                        error!("WebSocket error: {}", e);
                        break;
                    }
                    _ => {}
                }
            }
        });

        Ok(rx)
    }

    // Validator Operations
    pub async fn get_validator_set(&self, shard_id: u64) -> Result<Vec<Validator>> {
        self.request(
            "GET",
            &format!("/api/v1/validators?shard_id={}", shard_id),
            None,
        )
        .await
    }

    pub async fn stake(&self, amount: f64, validator_address: &str) -> Result<serde_json::Value> {
        self.request(
            "POST",
            "/api/v1/stake",
            Some(json!({
                "amount": amount,
                "validator_address": validator_address,
            })),
        )
        .await
    }

    // Bridge Operations
    pub async fn bridge_transfer(&self, request: BridgeTransferRequest) -> Result<BridgeTransfer> {
        self.request(
            "POST",
            "/api/v1/bridge/transfer",
            Some(serde_json::to_value(request)?),
        )
        .await
    }
} 