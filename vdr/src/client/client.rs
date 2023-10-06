use std::collections::HashMap;

use crate::{
    client::{
        implementation::web3::{client::Web3Client, contract::Web3Contract},
        types::{ContractParam, TransactionSpec},
        ContractConfig, ContractOutput, ContractSpec, Status, StatusResult, Transaction,
        TransactionType,
    },
    error::{VdrError, VdrResult},
    signer::Signer,
};

#[async_trait::async_trait]
pub trait Client {
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;
    async fn submit_transaction(&self, transaction: &[u8]) -> VdrResult<Vec<u8>>;
    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;
    async fn get_transaction_receipt(&self, hash: &[u8]) -> VdrResult<String>;
}

pub trait Contract {
    fn address(&self) -> String;
    fn encode_input(&self, method: &str, params: &[ContractParam]) -> VdrResult<Vec<u8>>;
    fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<ContractOutput>;
}

pub struct LedgerClient {
    chain_id: u64,
    client: Box<dyn Client>,
    contracts: HashMap<String, Box<dyn Contract>>,
}

impl LedgerClient {
    pub fn new(
        chain_id: u64,
        node_address: &str,
        contract_configs: &Vec<ContractConfig>,
        signer: Option<Box<dyn Signer + 'static + Send + Sync>>,
    ) -> VdrResult<LedgerClient> {
        let client = Web3Client::new(node_address, signer)?;
        let contracts = Self::init_contracts(&client, &contract_configs)?;
        Ok(LedgerClient {
            chain_id,
            client: Box::new(client),
            contracts,
        })
    }

    pub async fn ping(&self) -> VdrResult<StatusResult> {
        Ok(StatusResult { status: Status::Ok })
    }

    pub async fn sign_transaction(&self, transaction_spec: &TransactionSpec) -> VdrResult<Vec<u8>> {
        return self
            .client
            .sign_transaction(&transaction_spec.transaction)
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

    pub async fn get_transaction_receipt(&self, hash: &[u8]) -> VdrResult<String> {
        self.client.get_transaction_receipt(hash).await
    }

    pub fn chain_id(&self) -> u64 {
        self.chain_id
    }

    fn init_contracts(
        client: &Web3Client,
        contract_configs: &[ContractConfig],
    ) -> VdrResult<HashMap<String, Box<dyn Contract>>> {
        let mut contracts: HashMap<String, Box<dyn Contract>> = HashMap::new();
        for contract_config in contract_configs {
            let contract_spec = Self::read_contract_spec(&contract_config.spec_path)?;
            let contract = Web3Contract::new(client, &contract_config.address, &contract_spec)?;
            contracts.insert(contract_spec.name.clone(), Box::new(contract));
        }
        Ok(contracts)
    }

    fn read_contract_spec(spec_path: &str) -> VdrResult<ContractSpec> {
        let contract_spec = std::fs::read_to_string(spec_path).map_err(|err| {
            VdrError::Common(format!("Unable to read contract spec file. Err: {:?}", err))
        })?;
        let contract_spec: ContractSpec = serde_json::from_str(&contract_spec).map_err(|err| {
            VdrError::Common(format!(
                "Unable to parse contract specification. Err: {:?}",
                err.to_string()
            ))
        })?;
        Ok(contract_spec)
    }
}
