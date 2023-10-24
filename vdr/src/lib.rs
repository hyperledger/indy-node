mod client;
mod contracts;
mod error;
mod signer;
mod utils;

pub use client::{ContractConfig, LedgerClient};
pub use contracts::{
    CredentialDefinition, CredentialDefinitionRegistry, DidDocument, DidRegistry, Role,
    RoleControl, Schema, SchemaRegistry,
};

#[cfg(feature = "ledger_test")]
#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        client::test::client,
        contracts::{
            cl::{
                credential_definition::test::credential_definition, schema::test::schema,
                schema_registry::test::create_schema,
            },
            did::{did_doc::test::did_doc, did_registry::test::create_did},
        },
        error::VdrResult,
        signer::test::ACCOUNT,
    };

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

            // get receipt
            let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

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
            let _receipt = DidRegistry::create_did(&client, ACCOUNT, &did_doc)
                .await
                .unwrap();

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

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = create_did(&client).await;

            // write
            let schema = schema(&did_doc.id, None);
            let transaction =
                SchemaRegistry::build_create_schema_transaction(&client, ACCOUNT, &schema).unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();
            let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

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
            let did_doc = create_did(&client).await;

            // write
            let schema = schema(&did_doc.id, None);
            let _receipt = SchemaRegistry::create_schema(&client, ACCOUNT, &schema)
                .await
                .unwrap();

            // read
            let resolved_schema = SchemaRegistry::resolve_schema(&client, &schema.id)
                .await
                .unwrap();
            assert_eq!(schema, resolved_schema);

            Ok(())
        }
    }

    #[cfg(feature = "ledger_test")]
    mod credential_definition {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client();

            // create DID Document and Schema
            let did_doc = create_did(&client).await;
            let schema = create_schema(&client, &did_doc.id).await;

            // write
            let credential_definition = credential_definition(&did_doc.id, &schema.id, None);
            let transaction =
                CredentialDefinitionRegistry::build_create_credential_definition_transaction(
                    &client,
                    ACCOUNT,
                    &credential_definition,
                )
                .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();
            let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

            // read
            let transaction =
                CredentialDefinitionRegistry::build_resolve_credential_definition_transaction(
                    &client,
                    &credential_definition.id,
                )
                .unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let resolved_credential_definition =
                CredentialDefinitionRegistry::parse_resolve_credential_definition_result(
                    &client, &result,
                )
                .unwrap();
            assert_eq!(credential_definition, resolved_credential_definition);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_transaction_execution_test() -> VdrResult<()> {
            let client = client();

            // create DID Document
            let did_doc = create_did(&client).await;
            DidRegistry::resolve_did(&client, &did_doc.id)
                .await
                .unwrap();

            let schema = create_schema(&client, &did_doc.id).await;
            SchemaRegistry::resolve_schema(&client, &schema.id)
                .await
                .unwrap();

            // write
            let credential_definition = credential_definition(&did_doc.id, &schema.id, None);
            let _receipt = CredentialDefinitionRegistry::create_credential_definition(
                &client,
                ACCOUNT,
                &credential_definition,
            )
            .await
            .unwrap();

            // read
            let resolved_credential_definition =
                CredentialDefinitionRegistry::resolve_credential_definition(
                    &client,
                    &credential_definition.id,
                )
                .await
                .unwrap();
            assert_eq!(credential_definition, resolved_credential_definition);

            Ok(())
        }
    }

    #[cfg(feature = "ledger_test")]
    mod role {
        use super::*;

        async fn build_and_submit_assign_role_transaction(
            client: &LedgerClient,
            assignee_account: &str,
            role_to_assign: &Role,
        ) {
            // write
            let transaction = RoleControl::build_assign_role_transaction(
                client,
                ACCOUNT,
                role_to_assign,
                assignee_account,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            // get receipt
            let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

            // read
            let transaction =
                RoleControl::build_get_role_transaction(client, assignee_account).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let parsed_role = RoleControl::parse_get_role_result(&client, &result).unwrap();
            assert_eq!(*role_to_assign, parsed_role);
        }

        async fn build_and_submit_revoke_role_transaction(
            client: &LedgerClient,
            revokee_account: &str,
            role_to_revoke: &Role,
        ) {
            // write
            let transaction = RoleControl::build_revoke_role_transaction(
                client,
                ACCOUNT,
                role_to_revoke,
                revokee_account,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            // get receipt
            let receipt = client.get_transaction_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

            // read
            let transaction =
                RoleControl::build_has_role_transaction(client, role_to_revoke, revokee_account)
                    .unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let has_role = RoleControl::parse_has_role_result(&client, &result).unwrap();
            assert!(!has_role);
        }

        #[async_std::test]
        async fn demo_build_and_submit_assign_and_remove_role_transactions_test() -> VdrResult<()> {
            let client = client();
            let assignee_account = "0xed9d02e382b34818e88b88a309c7fe71e65f419d";
            let role_to_assign = Role::Endorser;

            build_and_submit_assign_role_transaction(&client, assignee_account, &role_to_assign)
                .await;

            build_and_submit_revoke_role_transaction(&client, assignee_account, &role_to_assign)
                .await;

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_assign_and_remove_role_execution_test() -> VdrResult<()> {
            let client = client();
            let assignee_account = "0xca843569e3427144cead5e4d5999a3d0ccf92b8e";
            let role_to_assign = Role::Trustee;

            // write
            let receipt =
                RoleControl::assign_role(&client, ACCOUNT, &role_to_assign, assignee_account)
                    .await
                    .unwrap();

            println!("Receipt: {}", receipt);

            // read
            let parsed_role = RoleControl::get_role(&client, assignee_account)
                .await
                .unwrap();
            assert_eq!(role_to_assign, parsed_role);

            // write
            let receipt =
                RoleControl::revoke_role(&client, ACCOUNT, &role_to_assign, assignee_account)
                    .await
                    .unwrap();

            println!("Receipt: {}", receipt);

            // read
            let has_role = RoleControl::has_role(&client, &role_to_assign, assignee_account)
                .await
                .unwrap();
            assert!(!has_role);

            Ok(())
        }
    }
}
