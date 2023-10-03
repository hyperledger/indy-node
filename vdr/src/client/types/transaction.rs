use crate::client::types::{Address, Bytes, U256, U64};

#[derive(Clone, Debug, Default, PartialEq)]
pub struct Transaction {
    pub nonce: Option<U256>,
    pub to: Address,
    pub value: U256,
    pub data: Vec<u8>,
    pub chain_id: Option<u64>,
    pub transaction_type: Option<U64>,
}

#[derive(Clone, Debug, PartialEq)]
pub enum TransactionType {
    Read,
    Write,
}

impl Default for TransactionType {
    fn default() -> Self {
        TransactionType::Read
    }
}

#[derive(Debug, Default, PartialEq)]
pub struct TransactionSpec {
    pub transaction_type: TransactionType,
    pub transaction: Transaction,
    pub signed_transaction: Option<Vec<u8>>,
}

impl TransactionSpec {
    pub fn set_signature(&mut self, signed_transaction: Vec<u8>) {
        self.signed_transaction = Some(signed_transaction)
    }
}
