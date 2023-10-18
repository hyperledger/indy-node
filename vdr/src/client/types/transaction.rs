use crate::{
    client::{ContractOutput, ContractParam},
    error::{VdrError, VdrResult},
    LedgerClient,
};

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

#[derive(Clone, Debug, Default, PartialEq)]
pub struct TransactionBuilder {
    contract: String,
    method: String,
    from: Option<String>,
    params: Vec<ContractParam>,
    type_: TransactionType,
}

impl TransactionBuilder {
    pub fn new() -> TransactionBuilder {
        TransactionBuilder::default()
    }

    pub fn set_contract(mut self, contract: &str) -> TransactionBuilder {
        self.contract = contract.to_string();
        self
    }

    pub fn set_method(mut self, method: &str) -> TransactionBuilder {
        self.method = method.to_string();
        self
    }

    pub fn add_param(mut self, param: ContractParam) -> TransactionBuilder {
        self.params.push(param);
        self
    }

    pub fn set_type(mut self, type_: TransactionType) -> TransactionBuilder {
        self.type_ = type_;
        self
    }

    pub fn set_from(mut self, from: &str) -> TransactionBuilder {
        self.from = Some(from.to_string());
        self
    }

    pub fn build(self, client: &LedgerClient) -> VdrResult<Transaction> {
        let contract = client.contract(&self.contract)?;
        let data = contract.encode_input(&self.method, &self.params)?;
        Ok(Transaction {
            type_: self.type_,
            from: self.from,
            to: contract.address(),
            chain_id: client.chain_id(),
            data,
            signed: None,
        })
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct TransactionParser {
    contract: String,
    method: String,
}

impl TransactionParser {
    pub fn new() -> TransactionParser {
        TransactionParser::default()
    }

    pub fn set_contract(mut self, contract: &str) -> TransactionParser {
        self.contract = contract.to_string();
        self
    }

    pub fn set_method(mut self, method: &str) -> TransactionParser {
        self.method = method.to_string();
        self
    }

    pub fn parse<T: TryFrom<ContractOutput, Error = VdrError>>(
        self,
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<T> {
        let contract = client.contract(&self.contract)?;
        let output = contract.decode_output(&self.method, bytes)?;
        if output.is_empty() {
            return Err(VdrError::Common(
                "Unable to parse object: Empty data".to_string(),
            ));
        }

        let data = output.get_tuple(0)?;
        T::try_from(data)
    }
}
