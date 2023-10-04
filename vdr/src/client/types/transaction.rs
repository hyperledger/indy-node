#[derive(Clone, Debug, Default, PartialEq)]
pub struct Transaction {
    pub to: String,
    pub chain_id: u64,
    pub data: Vec<u8>,
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
