use crate::client::Transaction;
use web3::types::{Bytes, TransactionParameters};

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
