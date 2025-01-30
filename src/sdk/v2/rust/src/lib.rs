pub mod client;
pub mod error;
pub mod types;

pub use client::VernachainClient;
pub use error::{Result, VernachainError};
pub use types::*;

/// Re-export commonly used types
pub mod prelude {
    pub use super::{
        Block, BridgeTransfer, BridgeTransferRequest, ContractDeployRequest, CrossShardTransfer,
        CrossShardTransferRequest, Result, SmartContract, Transaction, TransactionRequest,
        Validator, VernachainClient, VernachainError,
    };
} 