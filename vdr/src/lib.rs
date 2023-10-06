mod client;
mod contracts;
mod error;
mod signer;
mod utils;

pub use client::{ContractConfig, LedgerClient};
pub use contracts::{DidDocument, DidRegistry, Schema, SchemaRegistry};
pub use signer::BasicSigner;

pub use utils::{rand_string, sleep};

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        contracts::{
            DidDocument, DidRegistry, StringOrVector, VerificationKey, VerificationKeyType,
            VerificationMethod, VerificationMethodOrReference,
        },
        error::VdrResult,
    };

    const CHAIN_ID: u64 = 1337;
    const NODE_ADDRESS: &'static str = "http://127.0.0.1:8545";
    const PRIVATE_KEY: &'static str =
        "8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63";

    fn contracts() -> Vec<ContractConfig> {
        vec![
            ContractConfig {
                address: "0x0000000000000000000000000000000000003333".to_string(),
                spec_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/did/DidRegistry.sol/DidRegistry.json".to_string(),
            },
            ContractConfig {
                address: "0x0000000000000000000000000000000000005555".to_string(),
                spec_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/cl/SchemaRegistry.sol/SchemaRegistry.json".to_string(),
            },
        ]
    }

    fn did_doc() -> DidDocument {
        let method_id = rand_string();
        let id = format!("did:indy2:testnet:{}", method_id);
        DidDocument {
            context: StringOrVector::Vector(vec!["https://www.w3.org/ns/did/v1".to_string()]),
            id: id.clone(),
            controller: StringOrVector::Vector(vec![]),
            verification_method: vec![VerificationMethod {
                id: format!("{}#KEY-1", id),
                type_: VerificationKeyType::Ed25519VerificationKey2018,
                controller: id.clone(),
                verification_key: VerificationKey::Multibase {
                    public_key_multibase: "zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf"
                        .to_string(),
                },
            }],
            authentication: vec![VerificationMethodOrReference::String(format!(
                "{}#KEY-1",
                id
            ))],
            assertion_method: vec![],
            capability_invocation: vec![],
            capability_delegation: vec![],
            key_agreement: vec![],
            service: vec![],
            also_known_as: None,
        }
    }

    fn schema(issuer_id: &str) -> Schema {
        let name = rand_string();
        Schema {
            id: format!("{}/anoncreds/v0/SCHEMA/{}/1.0.0", issuer_id, name),
            issuer_id: issuer_id.to_string(),
            name,
            version: "1.0.0".to_string(),
            attr_names: vec!["First Name".to_string(), "Last Name".to_string()],
        }
    }

    pub fn client() -> LedgerClient {
        let signer = BasicSigner::new(PRIVATE_KEY).unwrap();
        let contracts = contracts();
        LedgerClient::new(CHAIN_ID, NODE_ADDRESS, &contracts, Some(Box::new(signer))).unwrap()
    }

    async fn get_transaction_receipt(client: &LedgerClient, hash: &[u8]) -> String {
        let receipt = client.get_transaction_receipt(hash).await.unwrap();
        println!("Receipt: {}", receipt);
        receipt
    }

    mod did {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_did_transaction_test() -> VdrResult<()> {
            let client = client();

            // write
            let did_doc = did_doc();
            let mut transaction_spec =
                DidRegistry::build_create_did_transaction(&client, &did_doc).unwrap();
            let signed_transaction = client.sign_transaction(&transaction_spec).await.unwrap();
            transaction_spec.set_signature(signed_transaction);
            let block_hash = client.submit_transaction(&transaction_spec).await.unwrap();
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let transaction_spec =
                DidRegistry::build_resolve_did_transaction(&client, &did_doc.id).unwrap();
            let result = client.submit_transaction(&transaction_spec).await.unwrap();
            let did_doc = DidRegistry::parse_resolve_did_result(&client, &result).unwrap();
            println!("did_doc {:?}", did_doc);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_did_transaction_execution_test() -> VdrResult<()> {
            let client = client();

            // write
            let did_doc = did_doc();
            let block_hash = DidRegistry::create_did(&client, &did_doc).await.unwrap();
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let did_doc = DidRegistry::resolve_did(&client, &did_doc.id)
                .await
                .unwrap();
            println!("did_doc {:?}", did_doc);

            Ok(())
        }
    }

    mod schema {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = did_doc();
            let block_hash = DidRegistry::create_did(&client, &did_doc).await.unwrap();

            // wait DID Document transaction will be committed
            sleep(3000);

            get_transaction_receipt(&client, &block_hash).await;

            // write
            let schema = schema(&did_doc.id);
            let mut transaction_spec =
                SchemaRegistry::build_create_schema_transaction(&client, &schema).unwrap();
            let signed_transaction = client.sign_transaction(&transaction_spec).await.unwrap();
            transaction_spec.set_signature(signed_transaction);
            let block_hash = client.submit_transaction(&transaction_spec).await.unwrap();

            // get transaction receipt
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let transaction_spec =
                SchemaRegistry::build_resolve_schema_transaction(&client, &schema.id).unwrap();
            let result = client.submit_transaction(&transaction_spec).await.unwrap();
            let schema = SchemaRegistry::parse_resolve_schema_result(&client, &result).unwrap();
            println!("schema {:?}", schema);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_transaction_execution_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = did_doc();
            let block_hash = DidRegistry::create_did(&client, &did_doc).await.unwrap();

            // wait DID Document transaction will be committed
            sleep(3000);

            // write
            let schema = schema(&did_doc.id);
            let block_hash = SchemaRegistry::create_schema(&client, &schema)
                .await
                .unwrap();

            // wait Schema transaction will be committed
            sleep(3000);

            // read
            let schema = SchemaRegistry::resolve_schema(&client, &schema.id)
                .await
                .unwrap();
            println!("schema {:?}", schema);

            Ok(())
        }
    }
}
