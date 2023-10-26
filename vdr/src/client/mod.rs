mod client;
mod constants;
mod implementation;
mod types;

use crate::error::VdrResult;

pub use client::*;
pub use constants::*;
pub use types::*;

#[async_trait::async_trait]
pub trait Client {
    /// Sign transaction.
    ///
    /// # Params
    /// - `transaction` prepared transaction to sign
    ///
    /// # Returns
    /// signed transaction object
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Transaction>;

    /// Submit signed write transaction to the ledger
    ///
    /// # Params
    /// - `transaction` prepared and signed transaction to submit
    ///
    /// # Returns
    /// hash of a block in which transaction included
    async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;

    /// Submit read transaction to the ledger
    ///
    /// # Params
    /// - `transaction` prepared transaction to submit
    ///
    /// # Returns
    /// result data of transaction execution
    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;

    /// Get the receipt for the given block hash
    ///
    /// # Params
    /// - `hash` hash of a block to get the receipt
    ///
    /// # Returns
    /// receipt as JSON string for the requested block
    async fn get_receipt(&self, hash: &[u8]) -> VdrResult<String>;

    /// Check client connection (passed node is alive and return valid ledger data)
    ///
    /// # Returns
    /// ledger status
    async fn ping(&self) -> VdrResult<PingStatus>;
}

pub trait Contract {
    /// Get the address of deployed contract
    ///
    /// # Returns
    /// address of the deployed contract. Should be used to execute contract methods
    fn address(&self) -> String;

    /// Encode data required for the execution of a contract method
    ///
    /// # Params
    /// - `method` method to execute
    /// - `params` data to pass/encode for contract execution
    ///
    /// # Returns
    /// encoded data to set into transaction
    fn encode_input(&self, method: &str, params: &[ContractParam]) -> VdrResult<Vec<u8>>;

    /// Decode the value (bytes) returned as the result of the execution of a contract method
    ///
    /// # Params
    /// - `method` method to execute
    /// - `output` data to decode (returned as result of sending call transaction)
    ///
    /// # Returns
    /// contract execution result in decoded form
    fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<ContractOutput>;
}
