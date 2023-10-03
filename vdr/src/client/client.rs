use std::collections::HashMap;

use crate::{
    client::{
        implementation::web3::{client_web3::Web3Client, contract_web3::Web3Contract},
        types::{Address, ContractParam, TransactionSpec},
        ContractSpec, StatusResult, Transaction, TransactionType,
    },
    error::{VdrError, VdrResult},
    signer::Signer,
};

#[async_trait::async_trait]
pub trait Client {
    async fn sign_transaction(
        &self,
        transaction: &Transaction,
        signer: &Signer,
    ) -> VdrResult<Vec<u8>>;
    async fn submit_transaction(&self, transaction: &Vec<u8>) -> VdrResult<Vec<u8>>;
    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;
}

pub trait Contract {
    fn address(&self) -> Address;
    fn encode_input(&self, method: &str, params: &[ContractParam]) -> VdrResult<Vec<u8>>;
    fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<Vec<ContractParam>>;
}

pub struct LedgerClient {
    client: Box<dyn Client>,
    contracts: HashMap<String, Box<dyn Contract>>,
    signer: Option<Signer>,
}

impl LedgerClient {
    pub fn new(
        node_address: &str,
        contract_specs: &Vec<ContractSpec>,
        signer: Option<Signer>,
    ) -> VdrResult<LedgerClient> {
        let client = Web3Client::new(node_address)?;

        let mut contracts: HashMap<String, Box<dyn Contract>> = HashMap::new();
        for contract_spec in contract_specs {
            contracts.insert(
                contract_spec.name.clone(),
                Box::new(Web3Contract::new(&client, contract_spec)?),
            );
        }

        Ok(LedgerClient {
            client: Box::new(client),
            contracts,
            signer,
        })
    }

    pub async fn ping(&self) -> VdrResult<StatusResult> {
        unimplemented!()
    }

    pub async fn sign_transaction(&self, transaction_spec: &TransactionSpec) -> VdrResult<Vec<u8>> {
        let signer = self.signer.as_ref().ok_or(VdrError::Unexpected)?;
        return self
            .client
            .sign_transaction(&transaction_spec.transaction, signer)
            .await;
    }

    pub async fn submit_transaction(
        &self,
        transaction_spec: &TransactionSpec,
    ) -> VdrResult<Vec<u8>> {
        match transaction_spec.transaction_type {
            TransactionType::Read => {
                self.client
                    .call_transaction(&transaction_spec.transaction)
                    .await
            }
            TransactionType::Write => {
                let signed_transaction = transaction_spec
                    .signed_transaction
                    .as_ref()
                    .ok_or(VdrError::Unexpected)?;
                self.client.submit_transaction(&signed_transaction).await
            }
        }
    }

    pub fn contract(&self, name: &str) -> VdrResult<&Box<dyn Contract>> {
        self.contracts.get(name).ok_or(VdrError::Unexpected)
    }
}
