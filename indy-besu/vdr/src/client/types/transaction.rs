use log::{trace, warn};

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

        trace!(
            "Set contract: {} to TransactionBuilder: {:?}",
            contract,
            self
        );

        self
    }

    pub fn set_method(mut self, method: &str) -> TransactionBuilder {
        self.method = method.to_string();

        trace!("Set method: {} to TransactionBuilder: {:?}", method, self);

        self
    }

    pub fn add_param(mut self, param: ContractParam) -> TransactionBuilder {
        self.params.push(param.clone());

        trace!(
            "Added ContractParam: {:?} to TransactionBuilder: {:?}",
            param,
            self
        );

        self
    }

    pub fn set_type(mut self, type_: TransactionType) -> TransactionBuilder {
        self.type_ = type_.clone();

        trace!(
            "Set TransactionType: {:?} to TransactionBuilder: {:?}",
            type_,
            self
        );

        self
    }

    pub fn set_from(mut self, from: &Address) -> TransactionBuilder {
        self.from = Some(from.clone());

        trace!("Set from: {:?} to TransactionBuilder: {:?}", from, self);

        self
    }

    pub fn build(self, client: &LedgerClient) -> VdrResult<Transaction> {
        let contract = client.contract(&self.contract)?;
        let data = contract.encode_input(&self.method, &self.params)?;

        let transaction = Transaction {
            type_: self.type_,
            from: self.from,
            to: contract.address(),
            chain_id: client.chain_id(),
            data,
            signed: None,
        };

        trace!("Built transaction: {:?}", transaction);

        Ok(transaction)
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

        trace!(
            "Set contract: {} to TransactionParser: {:?}",
            contract,
            self
        );

        self
    }

    pub fn set_method(mut self, method: &str) -> TransactionParser {
        self.method = method.to_string();

        trace!("Set method: {} to TransactionParser: {:?}", method, self);

        self
    }

    pub fn parse<T: TryFrom<ContractOutput, Error = VdrError>>(
        self,
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<T> {
        if bytes.is_empty() {
            let vdr_error =
                VdrError::ContractInvalidResponseData("Empty response bytes".to_string());

            warn!("Error: {:?} during transaction output parse", vdr_error);

            return Err(vdr_error);
        }
        let contract = client.contract(&self.contract)?;
        let output = contract.decode_output(&self.method, bytes)?;

        if output.is_empty() {
            let vdr_error =
                VdrError::ContractInvalidResponseData("Unable to parse response".to_string());

            warn!("Error: {:?} during transaction output parse", vdr_error);

            return Err(vdr_error);
        }

        trace!("Decoded transaction output: {:?}", output);

        T::try_from(output)
    }
}
