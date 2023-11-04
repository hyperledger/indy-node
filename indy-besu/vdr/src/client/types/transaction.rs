use crate::{
    client::{Address, ContractOutput, ContractParam},
    error::{VdrError, VdrResult},
    LedgerClient,
};

/// Type of transaction: write/read
/// depending on the transaction type different client methods will be executed to submit transaction
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

/// Transaction object
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Transaction {
    /// type of transaction: write/read
    /// depending on the transaction type different client methods will be executed to submit transaction
    pub type_: TransactionType,
    /// transaction sender account address
    pub from: Option<Address>,
    /// transaction recipient address
    pub to: String,
    /// chain id of the ledger
    pub chain_id: u64,
    /// transaction payload
    pub data: Vec<u8>,
    /// signed raw transaction
    pub signed: Option<Vec<u8>>,
}

impl Transaction {
    /// set signature for the transaction
    pub fn set_signature(&mut self, signature: &[u8]) {
        self.signed = Some(signature.to_owned())
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct TransactionBuilder {
    contract: String,
    method: String,
    from: Option<Address>,
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

    pub fn set_from(mut self, from: &Address) -> TransactionBuilder {
        self.from = Some(from.clone());
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
        if bytes.is_empty() {
            return Err(VdrError::ContractInvalidResponseData(
                "Empty response bytes".to_string(),
            ));
        }
        let contract = client.contract(&self.contract)?;
        let output = contract.decode_output(&self.method, bytes)?;

        if output.is_empty() {
            return Err(VdrError::ContractInvalidResponseData(
                "Unable to parse response".to_string(),
            ));
        }

        T::try_from(output)
    }
}
