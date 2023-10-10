#[derive(Clone, Debug, Default, PartialEq)]
pub struct Transaction {
    pub type_: TransactionType,
    pub from: Option<String>,
    pub to: String,
    pub chain_id: u64,
    pub data: Vec<u8>,
    pub signed: Option<Vec<u8>>,
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
