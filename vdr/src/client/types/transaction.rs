use crate::client::types::{Address, Bytes, U256, U64};
use web3::types::TransactionParameters;

#[derive(Clone, Debug, PartialEq)]
pub struct Transaction {
    pub nonce: Option<U256>,
    pub to: Address,
    pub value: U256,
    pub data: Vec<u8>,
    pub chain_id: Option<u64>,
    pub transaction_type: Option<U64>,
}

impl Default for Transaction {
    fn default() -> Self {
        Transaction {
            nonce: None,
            to: Default::default(),
            value: Default::default(),
            data: Default::default(),
            chain_id: None,
            transaction_type: None,
        }
    }
}

impl Into<TransactionParameters> for Transaction {
    fn into(self) -> TransactionParameters {
        TransactionParameters {
            nonce: self.nonce,
            to: Some(self.to),
            value: self.value,
            data: Bytes::from(self.data),
            chain_id: self.chain_id,
            transaction_type: self.transaction_type,
            ..Default::default()
        }
    }
}
