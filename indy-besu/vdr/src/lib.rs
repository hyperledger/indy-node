#[allow(clippy::module_inception)]
mod client;
mod contracts;
mod error;
mod signer;
mod utils;

#[cfg(feature = "migration")]
pub mod migration;
pub use client::{Address, Client, ContractConfig, LedgerClient, PingStatus, Status};
pub use contracts::{
    auth::{Role, RoleControl},
    cl::{
        credential_definition_registry::CredentialDefinitionRegistry,
        schema_registry::SchemaRegistry,
        types::{
            credential_definition::CredentialDefinition,
            credential_definition_id::CredentialDefinitionId, schema::Schema, schema_id::SchemaId,
        },
    },
    did::{
        did_registry::IndyDidRegistry,
        types::{
            did_doc::{DidDocument, VerificationKey, VerificationKeyType, DID},
            did_doc_builder::DidDocumentBuilder,
        },
    },
    network::ValidatorControl,
    StringOrVector,
};
pub use error::{VdrError, VdrResult};
pub use signer::Signer;

#[cfg(feature = "basic_signer")]
pub use signer::BasicSigner;

#[cfg(feature = "ledger_test")]
#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        client::{test::client, Address},
        contracts::{
            cl::{
                schema_registry::test::create_schema,
                types::{credential_definition::test::credential_definition, schema::test::schema},
            },
            did::{did_registry::test::create_did, types::did_doc::test::did_doc},
        },
        error::VdrResult,
        signer::basic_signer::test::{
            basic_signer, basic_signer_custom_key, TRUSTEE2_ACC, TRUSTEE2_PRIVATE_KEY, TRUSTEE_ACC,
            TRUSTEE_PRIVATE_KEY,
        },
    };

    mod did {
        use super::*;

        async fn create_client(private_key: &str) -> LedgerClient {
            let signer = basic_signer_custom_key(private_key);

            return client(Some(signer));
        }

        #[async_std::test]
        async fn demo_build_and_submit_did_transaction_test() -> VdrResult<()> {
            let client = client(None);

            // write
            let did_doc = did_doc(None);
            let transaction =
                IndyDidRegistry::build_create_did_transaction(&client, &TRUSTEE_ACC, &did_doc)
                    .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            // get receipt
            let receipt = client.get_receipt(&block_hash).await.unwrap();
            println!("Receipt: {}", receipt);

            // read
            let transaction =
                IndyDidRegistry::build_resolve_did_transaction(&client, &did_doc.id).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            let resolved_did_doc =
                IndyDidRegistry::parse_resolve_did_result(&client, &result).unwrap();
            assert_eq!(did_doc, resolved_did_doc);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_did_transaction_execution_test() -> VdrResult<()> {
            let client = client(None);

            // write
            let did_doc = did_doc(None);
            let _receipt = IndyDidRegistry::create_did(&client, &TRUSTEE_ACC, &did_doc)
                .await
                .unwrap();

            // read
            let resolved_did_doc = IndyDidRegistry::resolve_did(&client, &did_doc.id)
                .await
                .unwrap();
            assert_eq!(did_doc, resolved_did_doc);

            Ok(())
        }

        #[async_std::test]
        async fn add_and_deactivate_did_by_different_trustees_test() -> VdrResult<()> {
            let first_client = create_client(TRUSTEE_PRIVATE_KEY).await;
            let second_client = create_client(TRUSTEE2_PRIVATE_KEY).await;

            let did_doc = did_doc(None);
            let _receipt = IndyDidRegistry::create_did(&first_client, &TRUSTEE_ACC, &did_doc)
                .await
                .unwrap();

            let receipt =
                IndyDidRegistry::deactivate_did(&second_client, &TRUSTEE2_ACC, &did_doc.id)
                    .await
                    .unwrap();
            println!("Receipt: {}", receipt);

            Ok(())
        }

        #[async_std::test]
        async fn add_and_update_did_by_different_trustees_test() -> VdrResult<()> {
            let first_client = create_client(TRUSTEE_PRIVATE_KEY).await;
            let second_client = create_client(TRUSTEE2_PRIVATE_KEY).await;
            let mut did_doc = did_doc(None);

            let _receipt = IndyDidRegistry::create_did(&first_client, &TRUSTEE_ACC, &did_doc)
                .await
                .unwrap();

            let old_context = did_doc.context;
            did_doc.context = StringOrVector::String("https://www.w3.org/ns/did/v2".to_string());

            let receipt = IndyDidRegistry::update_did(&second_client, &TRUSTEE2_ACC, &did_doc)
                .await
                .unwrap();
            println!("Receipt: {}", receipt);

            let not_updated_did_doc = IndyDidRegistry::resolve_did(&first_client, &did_doc.id)
                .await
                .unwrap();

            assert_eq!(old_context, not_updated_did_doc.context);

            Ok(())
        }
    }

    mod schema {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client(None);

            // create DID Document
            let did_doc = create_did(&client).await;

            // write
            let schema = schema(&did_doc.id, None);
            let transaction =
                SchemaRegistry::build_create_schema_transaction(&client, &TRUSTEE_ACC, &schema)
                    .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();
            let receipt = client.get_receipt(&block_hash).await.unwrap();
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
            let client = client(None);

            // create DID Document
            let did_doc = create_did(&client).await;

            // write
            let schema = schema(&did_doc.id, None);
            let _receipt = SchemaRegistry::create_schema(&client, &TRUSTEE_ACC, &schema)
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

    mod credential_definition {
        use super::*;

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let client = client(None);

            // create DID Document and Schema
            let did_doc = create_did(&client).await;
            let schema = create_schema(&client, &did_doc.id).await;

            // write
            let credential_definition = credential_definition(&did_doc.id, &schema.id, None);
            let transaction =
                CredentialDefinitionRegistry::build_create_credential_definition_transaction(
                    &client,
                    &TRUSTEE_ACC,
                    &credential_definition,
                )
                .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();
            let receipt = client.get_receipt(&block_hash).await.unwrap();
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
            let client = client(None);

            // create DID Document
            let did_doc = create_did(&client).await;
            IndyDidRegistry::resolve_did(&client, &did_doc.id)
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
                &TRUSTEE_ACC,
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

    mod role {
        use super::*;

        pub(crate) async fn build_and_submit_assign_role_transaction(
            client: &LedgerClient,
            assignee_account: &Address,
            role_to_assign: &Role,
        ) -> String {
            let transaction = RoleControl::build_assign_role_transaction(
                client,
                &TRUSTEE_ACC,
                role_to_assign,
                assignee_account,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            client.get_receipt(&block_hash).await.unwrap()
        }

        async fn build_and_submit_revoke_role_transaction(
            client: &LedgerClient,
            revokee_account: &Address,
            role_to_revoke: &Role,
        ) -> String {
            let transaction = RoleControl::build_revoke_role_transaction(
                client,
                &TRUSTEE_ACC,
                role_to_revoke,
                revokee_account,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            client.get_receipt(&block_hash).await.unwrap()
        }

        async fn build_and_submit_get_role_transaction(
            client: &LedgerClient,
            assignee_account: &Address,
        ) -> Role {
            let transaction =
                RoleControl::build_get_role_transaction(client, assignee_account).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            RoleControl::parse_get_role_result(&client, &result).unwrap()
        }

        async fn build_and_submit_has_role_transaction(
            client: &LedgerClient,
            role: &Role,
            assignee_account: &Address,
        ) -> bool {
            let transaction =
                RoleControl::build_has_role_transaction(client, role, assignee_account).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();
            RoleControl::parse_has_role_result(&client, &result).unwrap()
        }

        #[async_std::test]
        async fn demo_build_and_submit_assign_and_remove_role_transactions_test() -> VdrResult<()> {
            let signer = basic_signer();
            let (assignee_account, _) = signer.create_account(None).unwrap();
            let client = client(Some(signer));
            let role_to_assign = Role::Endorser;

            let receipt = build_and_submit_assign_role_transaction(
                &client,
                &assignee_account,
                &role_to_assign,
            )
            .await;
            println!("Receipt: {}", receipt);

            let assigned_role =
                build_and_submit_get_role_transaction(&client, &assignee_account).await;
            assert_eq!(role_to_assign, assigned_role);

            let receipt = build_and_submit_revoke_role_transaction(
                &client,
                &assignee_account,
                &role_to_assign,
            )
            .await;
            println!("Receipt: {}", receipt);

            let has_role =
                build_and_submit_has_role_transaction(&client, &role_to_assign, &assignee_account)
                    .await;
            assert!(!has_role);

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_assign_and_remove_role_execution_test() -> VdrResult<()> {
            let signer = basic_signer();
            let (assignee_account, _) = signer.create_account(None).unwrap();
            let client = client(Some(signer));
            let role_to_assign = Role::Trustee;

            // write
            let receipt =
                RoleControl::assign_role(&client, &TRUSTEE_ACC, &role_to_assign, &assignee_account)
                    .await
                    .unwrap();

            println!("Receipt: {}", receipt);

            // read
            let parsed_role = RoleControl::get_role(&client, &assignee_account)
                .await
                .unwrap();
            assert_eq!(role_to_assign, parsed_role);

            // write
            let receipt =
                RoleControl::revoke_role(&client, &TRUSTEE_ACC, &role_to_assign, &assignee_account)
                    .await
                    .unwrap();
            println!("Receipt: {}", receipt);

            // read
            let has_role = RoleControl::has_role(&client, &role_to_assign, &assignee_account)
                .await
                .unwrap();
            assert!(!has_role);

            Ok(())
        }
    }

    mod validator {
        use crate::{
            contracts::network::ValidatorAddresses, signer::basic_signer::test::basic_signer,
        };

        use super::*;

        async fn build_and_submit_get_validators_transaction(
            client: &LedgerClient,
        ) -> ValidatorAddresses {
            let transaction = ValidatorControl::build_get_validators_transaction(&client).unwrap();
            let result = client.submit_transaction(&transaction).await.unwrap();

            ValidatorControl::parse_get_validators_result(&client, &result).unwrap()
        }

        async fn build_and_submit_add_validator_transaction(
            client: &LedgerClient,
            new_validator_address: &Address,
        ) -> String {
            let transaction = ValidatorControl::build_add_validator_transaction(
                &client,
                &TRUSTEE_ACC,
                new_validator_address,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            client.get_receipt(&block_hash).await.unwrap()
        }

        async fn build_and_submit_remove_validator_transaction(
            client: &LedgerClient,
            validator_address: &Address,
        ) -> String {
            // write
            let transaction = ValidatorControl::build_remove_validator_transaction(
                &client,
                &TRUSTEE_ACC,
                validator_address,
            )
            .unwrap();
            let signed_transaction = client.sign_transaction(&transaction).await.unwrap();
            let block_hash = client
                .submit_transaction(&signed_transaction)
                .await
                .unwrap();

            client.get_receipt(&block_hash).await.unwrap()
        }

        #[async_std::test]
        async fn demo_build_and_submit_transaction_test() -> VdrResult<()> {
            let signer = basic_signer();
            let (new_validator_address, _) = signer.create_account(None).unwrap();
            let client = client(Some(signer));
            role::build_and_submit_assign_role_transaction(&client, &TRUSTEE_ACC, &Role::Steward)
                .await;

            let receipt =
                build_and_submit_add_validator_transaction(&client, &new_validator_address).await;
            println!("Receipt: {}", receipt);

            let validator_list = build_and_submit_get_validators_transaction(&client).await;
            assert_eq!(validator_list.len(), 5);
            assert!(validator_list.contains(&new_validator_address));

            let receipt =
                build_and_submit_remove_validator_transaction(&client, &new_validator_address)
                    .await;
            println!("Receipt: {}", receipt);

            let validator_list = build_and_submit_get_validators_transaction(&client).await;
            assert_eq!(validator_list.len(), 4);
            assert!(!validator_list.contains(&new_validator_address));

            Ok(())
        }

        #[async_std::test]
        async fn demo_single_step_transaction_execution_test() -> VdrResult<()> {
            let signer = basic_signer();
            let (new_validator_address, _) = signer.create_account(None).unwrap();
            let client = client(Some(signer));
            role::build_and_submit_assign_role_transaction(&client, &TRUSTEE_ACC, &Role::Steward)
                .await;

            ValidatorControl::add_validator(&client, &TRUSTEE_ACC, &new_validator_address)
                .await
                .unwrap();

            let validator_list = ValidatorControl::get_validators(&client).await.unwrap();
            assert_eq!(validator_list.len(), 5);
            assert!(validator_list.contains(&new_validator_address));

            ValidatorControl::remove_validator(&client, &TRUSTEE_ACC, &new_validator_address)
                .await
                .unwrap();

            let validator_list = ValidatorControl::get_validators(&client).await.unwrap();
            assert_eq!(validator_list.len(), 4);
            assert!(!validator_list.contains(&new_validator_address));

            Ok(())
        }
    }
}
