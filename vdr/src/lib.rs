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
        client::test::client,
        contracts::did::test::did_doc,
        error::VdrResult,
        signer::test::ACCOUNT
    };

    async fn get_transaction_receipt(client: &LedgerClient, hash: &[u8]) -> String {
        let receipt = client.get_transaction_receipt(hash).await.unwrap();
        println!("Receipt: {}", receipt);
        receipt
    }

    #[cfg(feature = "ledger_test")]
    mod did {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_did_transaction_test() -> VdrResult<()> {
            let client = client();

            // write
            let did_doc = did_doc(None);
            let transaction =
                DidRegistry::build_create_did_transaction(&client, ACCOUNT, &did_doc).unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let transaction =
                DidRegistry::build_resolve_did_transaction(&client, &did_doc.id).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let resolved_did_doc = DidRegistry::parse_resolve_did_result(&client, &result).unwrap();
            assert_eq!(did_doc, resolved_did_doc);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_did_transaction_execution_test() -> VdrResult<()> {
            let client = client();

            // write
            let did_doc = did_doc(None);
            let block_hash = DidRegistry::create_did(&client, ACCOUNT, &did_doc)
                .await
                .unwrap();
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let resolved_did_doc = DidRegistry::resolve_did(&client, &did_doc.id)
                .await
                .unwrap();
            assert_eq!(did_doc, resolved_did_doc);

            Ok(())
        }
    }

    #[cfg(feature = "ledger_test")]
    mod schema {
        use super::*;
        use crate::contracts::cl::schema::test::schema;

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = did_doc(None);
            let block_hash = DidRegistry::create_did(&client, ACCOUNT, &did_doc)
                .await
                .unwrap();

            // wait DID Document transaction will be committed
            sleep(6000);

            get_transaction_receipt(&client, &block_hash).await;

            // write
            let schema = schema(&did_doc.id, None);
            let transaction =
                SchemaRegistry::build_create_schema_transaction(&client, ACCOUNT, &schema).unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            // get transaction receipt
            sleep(6000);
            get_transaction_receipt(&client, block_hash.as_slice()).await;

            // read
            let transaction =
                SchemaRegistry::build_resolve_schema_transaction(&client, &schema.id).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let resolved_schema =
                SchemaRegistry::parse_resolve_schema_result(&client, &result).unwrap();
            assert_eq!(schema, resolved_schema);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_transaction_execution_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = did_doc(None);
            let block_hash = DidRegistry::create_did(&client, ACCOUNT, &did_doc)
                .await
                .unwrap();

            // wait DID Document transaction will be committed
            sleep(3000);
            get_transaction_receipt(&client, &block_hash).await;

            // write
            let schema = schema(&did_doc.id, None);
            let block_hash = SchemaRegistry::create_schema(&client, ACCOUNT, &schema)
                .await
                .unwrap();

            // wait Schema transaction will be committed
            sleep(3000);
            get_transaction_receipt(&client, &block_hash).await;

            // read
            let resolved_schema = SchemaRegistry::resolve_schema(&client, &schema.id)
                .await
                .unwrap();
            assert_eq!(schema, resolved_schema);

            Ok(())
        }
    }
}
