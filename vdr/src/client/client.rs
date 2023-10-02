use std::collections::HashMap;

use crate::{
    client::{
        implementation::web3::{client_web3::Web3Client, contract_web3::Web3Contract},
        types::{Address, ContractParam, Transaction},
    },
    signer::Signer,
};

#[async_trait::async_trait]
pub trait Client {
    async fn sign_transaction(&self, transaction: Transaction, signer: &Signer) -> Vec<u8>;
    async fn send_raw_transaction(&self, transaction: &[u8]) -> String;
    async fn call(&self, transaction: &Transaction) -> Vec<u8>;
}

pub trait Contract {
    fn address(&self) -> Address;
    fn encode_input(&self, method: &str, params: &[ContractParam]) -> Vec<u8>;
    fn decode_output(&self, method: &str, output: &[u8]) -> Vec<ContractParam>;
}

pub struct LedgerClient {
    client: Box<dyn Client>,
    contracts: HashMap<String, Box<dyn Contract>>,
}

pub struct ContractSpec {
    pub name: String,
    pub address: String,
    pub abi_path: String,
}

impl LedgerClient {
    pub fn new(node_address: &str, contract_specs: &Vec<ContractSpec>) -> Box<LedgerClient> {
        let client = Web3Client::new(node_address);

        let mut contracts: HashMap<String, Box<dyn Contract>> = HashMap::new();
        for contract_spec in contract_specs {
            contracts.insert(
                contract_spec.name.clone(),
                Box::new(Web3Contract::new(&client, contract_spec)),
            );
        }

        return Box::new(LedgerClient {
            client: Box::new(client),
            contracts,
        });
    }

    pub async fn sign_transaction(&self, transaction: Transaction, signer: &Signer) -> Vec<u8> {
        return self.client.sign_transaction(transaction, signer).await;
    }

    pub async fn submit(&self, transaction: &[u8]) -> String {
        return self.client.send_raw_transaction(transaction).await;
    }

    pub async fn call(&self, transaction: &Transaction) -> Vec<u8> {
        return self.client.call(transaction).await;
    }

    pub fn contract(&self, name: &str) -> &Box<dyn Contract> {
        self.contracts.get(name).unwrap()
    }
}
