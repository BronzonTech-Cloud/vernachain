use thiserror::Error;

#[derive(Error, Debug)]
pub enum VernachainError {
    #[error("HTTP request failed: {0}")]
    HttpError(#[from] reqwest::Error),

    #[error("WebSocket error: {0}")]
    WebSocketError(#[from] tokio_tungstenite::tungstenite::Error),

    #[error("JSON serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Invalid API key")]
    AuthenticationError,

    #[error("Validation error: {0}")]
    ValidationError(String),

    #[error("Network error: {0}")]
    NetworkError(String),

    #[error("Unexpected response format: {0}")]
    UnexpectedResponseError(String),

    #[error("WebSocket connection closed")]
    WebSocketClosed,

    #[error("Operation timeout")]
    TimeoutError,

    #[error("Rate limit exceeded")]
    RateLimitError,

    #[error("Internal error: {0}")]
    InternalError(String),
}

pub type Result<T> = std::result::Result<T, VernachainError>; 