use crate::wallet::BesuWallet;
use indy2_vdr::{
    ContractConfig, CredentialDefinition, CredentialDefinitionId, CredentialDefinitionRegistry,
    LedgerClient, Schema, SchemaId, SchemaRegistry, Status,
};
use serde_json::json;
use std::{env, fs};
use vdrtoolsrs::{future::Future, PoolHandle};

pub enum Ledgers {
    Indy,
    Besu,
}

pub struct IndyLedger {
    pub handle: PoolHandle,
}

impl IndyLedger {
    pub fn new(name: &str) -> IndyLedger {
        let mut cur_dir = env::current_dir().unwrap();
        cur_dir.push("docker.txn");
        let genesis_txn = fs::canonicalize(&cur_dir)
            .unwrap()
            .to_str()
            .unwrap()
            .to_string();

        let config = json!({ "genesis_txn": genesis_txn }).to_string();
        vdrtoolsrs::pool::create_pool_ledger_config(name, Some(&config))
            .wait()
            .ok();
        let handle = vdrtoolsrs::pool::open_pool_ledger(name, None)
            .wait()
            .unwrap();
        IndyLedger { handle }
    }

    pub fn get_schema(&self, id: &str) -> (String, String) {
        let request = vdrtoolsrs::ledger::build_get_schema_request(None, id)
            .wait()
            .unwrap();
        let response = vdrtoolsrs::ledger::submit_request(self.handle, &request)
            .wait()
            .unwrap();
        let (schema_id, schema) = vdrtoolsrs::ledger::parse_get_schema_response(&response)
            .wait()
            .unwrap();
        (schema_id, schema)
    }

    pub fn get_cred_def(&self, id: &str) -> (String, String) {
        let request = vdrtoolsrs::ledger::build_get_cred_def_request(None, id)
            .wait()
            .unwrap();
        let response = vdrtoolsrs::ledger::submit_request(self.handle, &request)
            .wait()
            .unwrap();
        let (schema_id, schema) = vdrtoolsrs::ledger::parse_get_cred_def_response(&response)
            .wait()
            .unwrap();
        (schema_id, schema)
    }
}

pub struct BesuLedger {
    pub client: LedgerClient,
}

impl BesuLedger {
    pub const CHAIN_ID: u64 = 1337;
    pub const NODE_ADDRESS: &'static str = "http://127.0.0.1:8545";
    pub const CONTRACTS_SPEC_BASE_PATH: &'static str = "../../smart_contracts/artifacts/contracts/";
    pub const DID_REGISTRY_ADDRESS: &'static str = "0x0000000000000000000000000000000000003333";
    pub const DID_REGISTRY_SPEC_PATH: &'static str = "did/DidRegistry.sol/DidRegistry.json";
    pub const SCHEMA_REGISTRY_ADDRESS: &'static str = "0x0000000000000000000000000000000000005555";
    pub const SCHEMA_REGISTRY_SPEC_PATH: &'static str = "cl/SchemaRegistry.sol/SchemaRegistry.json";
    pub const CRED_DEF_REGISTRY_ADDRESS: &'static str =
        "0x0000000000000000000000000000000000004444";
    pub const CRED_DEF_REGISTRY_SPEC_PATH: &'static str =
        "cl/CredentialDefinitionRegistry.sol/CredentialDefinitionRegistry.json";

    fn build_contract_path(contract_path: &str) -> String {
        let mut cur_dir = env::current_dir().unwrap();
        cur_dir.push(Self::CONTRACTS_SPEC_BASE_PATH);
        cur_dir.push(contract_path);
        fs::canonicalize(&cur_dir)
            .unwrap()
            .to_str()
            .unwrap()
            .to_string()
    }

    fn contracts() -> Vec<ContractConfig> {
        vec![
            ContractConfig {
                address: Self::DID_REGISTRY_ADDRESS.to_string(),
                spec_path: Self::build_contract_path(Self::DID_REGISTRY_SPEC_PATH),
            },
            ContractConfig {
                address: Self::SCHEMA_REGISTRY_ADDRESS.to_string(),
                spec_path: Self::build_contract_path(Self::SCHEMA_REGISTRY_SPEC_PATH),
            },
            ContractConfig {
                address: Self::CRED_DEF_REGISTRY_ADDRESS.to_string(),
                spec_path: Self::build_contract_path(Self::CRED_DEF_REGISTRY_SPEC_PATH),
            },
        ]
    }

    pub async fn new(wallet: BesuWallet) -> BesuLedger {
        let client = LedgerClient::new(
            Self::CHAIN_ID,
            Self::NODE_ADDRESS,
            &Self::contracts(),
            Some(Box::new(wallet.signer)),
        )
        .unwrap();
        let status = client.ping().await.unwrap();
        assert_eq!(Status::Ok, status.status, "Besu network is not reachable");

        BesuLedger { client }
    }

    pub async fn get_schema(&self, id: &SchemaId) -> Schema {
        SchemaRegistry::resolve_schema(&self.client, id)
            .await
            .unwrap()
    }

    pub async fn get_cred_def(&self, id: &CredentialDefinitionId) -> CredentialDefinition {
        CredentialDefinitionRegistry::resolve_credential_definition(&self.client, id)
            .await
            .unwrap()
    }
}
