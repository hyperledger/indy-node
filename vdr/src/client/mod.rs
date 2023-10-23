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
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Transaction>;
    async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;
    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;
    async fn get_transaction_receipt(&self, hash: &[u8]) -> VdrResult<String>;
    async fn ping(&self) -> VdrResult<PingStatus>;
}

pub trait Contract {
    fn address(&self) -> String;
    fn encode_input(&self, method: &str, params: &[ContractParam]) -> VdrResult<Vec<u8>>;
    fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<ContractOutput>;
}
