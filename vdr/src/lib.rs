mod client;
mod contracts;
mod error;
mod signer;
mod utils;

pub use client::{ContractConfig, LedgerClient};
pub use contracts::{Schema, SchemaRegistry};
pub use signer::BasicSigner;

pub use utils::{rand_string, sleep};

#[cfg(test)]
mod tests {
    use crate::error::VdrResult;
    use super::*;

    const CHAIN_ID: u64 = 1337;
    const NODE_ADDRESS: &'static str = "http://127.0.0.1:8545";
    const PRIVATE_KEY: &'static str =
        "8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63";

    fn contracts() -> Vec<ContractConfig> {
        vec![
            ContractConfig {
                address: "0x0000000000000000000000000000000000005555".to_string(),
                spec_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/cl/SchemaRegistry.sol/SchemaRegistry.json".to_string(),
            }
        ]
    }

    fn schema_id() -> String {
        format!(
            "did:indy2:testnet:SEp33q43PsdP7nDATyySSH/anoncreds/v0/SCHEMA/{:?}/1.0",
            rand_string()
        )
    }

    fn schema() -> Schema {
        Schema {
            name: "test".to_string(),
        }
    }

    #[async_std::test]
    async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
        let signer = BasicSigner::new(PRIVATE_KEY).unwrap();
        let contracts = contracts();
        let client =
            LedgerClient::new(CHAIN_ID, NODE_ADDRESS, &contracts, Some(Box::new(signer))).unwrap();

        // write
        let id = r#"did:indy2:testnet:SEp33q43PsdP7nDATyySSH/anoncreds/v0/SCHEMA/"mz4ys71"/1.0"#;
        println!("Schema id: {}", id);
        let schema = schema();
        let mut transaction_spec =
            SchemaRegistry::build_create_schema_transaction(&client, &id, &schema).unwrap();
        let signed_transaction = client.sign_transaction(&transaction_spec).await.unwrap();
        transaction_spec.set_signature(signed_transaction);
        let block_hash = client.submit_transaction(&transaction_spec).await.unwrap();
        println!("block_hash {:?}", block_hash);

        sleep(6000);

        let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
        println!("Receipt: {}", receipt);

        // read
        let transaction_spec =
            SchemaRegistry::build_resolve_schema_transaction(&client, &id).unwrap();
        let result = client.submit_transaction(&transaction_spec).await.unwrap();
        let schema = SchemaRegistry::parse_resolve_schema_result(&client, &result).unwrap();
        println!("schema {:?}", schema);

        Ok(())
    }

    #[async_std::test]
    async fn demo_single_step_transaction_execution_test() -> VdrResult<()> {
        let signer = BasicSigner::new(PRIVATE_KEY).unwrap();
        let contracts = contracts();
        let client =
            LedgerClient::new(CHAIN_ID, NODE_ADDRESS, &contracts, Some(Box::new(signer))).unwrap();

        // write
        let id = schema_id();
        let schema = schema();
        let result = SchemaRegistry::create_schema(&client, &id, &schema)
            .await
            .unwrap();
        println!("result {:?}", result);

        sleep(6000);

        // read
        let schema = SchemaRegistry::resolve_schema(&client, &id).await.unwrap();
        println!("schema {:?}", schema);

        Ok(())
    }
}
