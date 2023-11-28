use log::{debug, info};

use crate::{
    client::{
        Address, ContractParam, LedgerClient, Transaction, TransactionBuilder, TransactionParser,
        TransactionType,
    },
    contracts::cl::types::{
        credential_definition::{CredentialDefinition, CredentialDefinitionWithMeta},
        credential_definition_id::CredentialDefinitionId,
    },
    error::VdrResult,
};

/// CredentialDefinitionRegistry contract methods
pub struct CredentialDefinitionRegistry;

impl CredentialDefinitionRegistry {
    const CONTRACT_NAME: &'static str = "CredentialDefinitionRegistry";
    const METHOD_CREATE_CREDENTIAL_DEFINITION: &'static str = "createCredentialDefinition";
    const METHOD_RESOLVE_CREDENTIAL_DEFINITION: &'static str = "resolveCredentialDefinition";

    /// Build transaction to execute CredentialDefinitionRegistry.createCredentialDefinition contract
    /// method to create a new Credential Definition
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `credential_definition` Credential Definition object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:credential-definition
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_create_credential_definition_transaction(
        client: &LedgerClient,
        from: &Address,
        credential_definition: &CredentialDefinition,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, CredentialDefinition: {:?}",
            Self::METHOD_CREATE_CREDENTIAL_DEFINITION,
            from.value(),
            credential_definition
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_CREATE_CREDENTIAL_DEFINITION)
            .add_param(credential_definition.clone().into())
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_CREATE_CREDENTIAL_DEFINITION,
            transaction
        );

        transaction
    }

    /// Build transaction to execute CredentialDefinitionRegistry.resolveCredentialDefinition contract
    /// method to retrieve an existing Credential Definition by the given id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `id` id of Credential Definition to resolve
    ///
    /// # Returns
    /// Read transaction to submit
    pub fn build_resolve_credential_definition_transaction(
        client: &LedgerClient,
        id: &CredentialDefinitionId,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. CredentialDefinitionId: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            id
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION)
            .add_param(ContractParam::String(id.value().into()))
            .set_type(TransactionType::Read)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            transaction
        );

        transaction
    }

    /// Parse the result of execution CredentialDefinitionRegistry.resolveCredentialDefinition contract
    /// method to receive a Credential Definition associated with the id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `bytes` result bytes returned from the ledger
    ///
    /// # Returns
    /// parsed Credential Definition
    pub fn parse_resolve_credential_definition_result(
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<CredentialDefinition> {
        debug!(
            "{} result parse has started. Bytes to parse: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            bytes
        );

        let result = TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION)
            .parse::<CredentialDefinitionWithMeta>(client, bytes)
            .map(|credential_definition_with_meta| {
                credential_definition_with_meta.credential_definition
            });

        info!(
            "{} result parse has finished. Result: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            result
        );

        result
    }

    /// Single step function executing CredentialDefinitionRegistry.createCredentialDefinition smart contract
    /// method to create a new Credential Definition
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `credential_definition` Credential Definition object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:credential-definition
    ///
    /// # Returns
    /// receipt of executed transaction
    pub async fn create_credential_definition(
        client: &LedgerClient,
        from: &Address,
        credential_definition: &CredentialDefinition,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Sender: {}, CredentialDefenition: {:?}",
            Self::METHOD_CREATE_CREDENTIAL_DEFINITION,
            from.value(),
            credential_definition
        );

        let transaction = Self::build_create_credential_definition_transaction(
            client,
            from,
            credential_definition,
        )?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_CREATE_CREDENTIAL_DEFINITION,
            receipt
        );

        receipt
    }

    /// Single step function executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract
    /// method to resolve Credential Definition for an existing id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `id` id of Credential Definition to resolve
    ///
    /// # Returns
    /// resolved Credential Definition
    pub async fn resolve_credential_definition(
        client: &LedgerClient,
        id: &CredentialDefinitionId,
    ) -> VdrResult<CredentialDefinition> {
        debug!(
            "{} process has started. CredentialDefenitionId: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            id
        );

        let transaction = Self::build_resolve_credential_definition_transaction(client, id)?;
        let result = client.submit_transaction(&transaction).await?;
        let parsed_result = Self::parse_resolve_credential_definition_result(client, &result);

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION,
            parsed_result
        );

        parsed_result
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        client::test::{client, CHAIN_ID, CRED_DEF_REGISTRY_ADDRESS},
        contracts::{
            cl::types::{
                credential_definition::test::{credential_definition, CREDENTIAL_DEFINITION_TAG},
                schema::test::SCHEMA_ID,
                schema_id::SchemaId,
            },
            did::types::did_doc::test::ISSUER_ID,
        },
        signer::basic_signer::test::TRUSTEE_ACC,
        utils::init_env_logger,
        DID,
    };

    mod build_create_credential_definition_transaction {
        use super::*;

        #[test]
        fn build_create_credential_definition_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction =
                CredentialDefinitionRegistry::build_create_credential_definition_transaction(
                    &client,
                    &TRUSTEE_ACC,
                    &credential_definition(
                        &DID::new(ISSUER_ID),
                        &SchemaId::new(SCHEMA_ID),
                        Some(CREDENTIAL_DEFINITION_TAG),
                    ),
                )
                .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
                to: CRED_DEF_REGISTRY_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: vec![
                    156, 53, 148, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 128, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 2, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 224, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 151, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110,
                    101, 116, 58, 51, 76, 112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84,
                    104, 103, 101, 50, 53, 70, 90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100,
                    115, 47, 118, 48, 47, 67, 76, 65, 73, 77, 95, 68, 69, 70, 47, 100, 105, 100,
                    58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76,
                    112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53,
                    70, 90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47,
                    83, 67, 72, 69, 77, 65, 47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116,
                    47, 49, 46, 48, 46, 48, 47, 100, 101, 102, 97, 117, 108, 116, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 40, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58, 116,
                    101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115, 122, 107, 103, 84,
                    109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79, 100, 105,
                    100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51,
                    76, 112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50,
                    53, 70, 90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48,
                    47, 83, 67, 72, 69, 77, 65, 47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51,
                    116, 47, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 2, 67, 76, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 100, 101, 102, 97, 117,
                    108, 116, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 68, 123, 34, 110, 34, 58, 34, 55, 55, 57, 46, 46, 46, 51,
                    57, 55, 34, 44, 34, 114, 99, 116, 120, 116, 34, 58, 34, 55, 55, 52, 46, 46, 46,
                    57, 55, 55, 34, 44, 34, 115, 34, 58, 34, 55, 53, 48, 46, 46, 56, 57, 51, 34,
                    44, 34, 122, 34, 58, 34, 54, 51, 50, 46, 46, 46, 48, 48, 53, 34, 125, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                ],
                signed: None,
            };
            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_resolve_credential_definition_transaction {
        use super::*;

        #[test]
        fn build_resolve_credential_definition_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction =
                CredentialDefinitionRegistry::build_resolve_credential_definition_transaction(
                    &client,
                    &credential_definition(
                        &DID::new(ISSUER_ID),
                        &SchemaId::new(SCHEMA_ID),
                        Some(CREDENTIAL_DEFINITION_TAG),
                    )
                    .id,
                )
                .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Read,
                from: None,
                to: CRED_DEF_REGISTRY_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: vec![
                    97, 112, 196, 138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 151, 100, 105, 100, 58, 105,
                    110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106,
                    115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90,
                    119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47, 67, 76,
                    65, 73, 77, 95, 68, 69, 70, 47, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58,
                    116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115, 122, 107, 103,
                    84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 47, 97, 110, 111,
                    110, 99, 114, 101, 100, 115, 47, 118, 48, 47, 83, 67, 72, 69, 77, 65, 47, 70,
                    49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116, 47, 49, 46, 48, 46, 48, 47,
                    100, 101, 102, 97, 117, 108, 116, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                ],
                signed: None,
            };
            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_resolve_credential_definition_result {
        use super::*;

        #[test]
        fn parse_resolve_credential_definition_result_test() {
            init_env_logger();
            let client = client(None);
            let data = vec![
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 101, 39, 237, 185, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 128, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 2, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 151, 100, 105,
                100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76,
                112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70,
                90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47, 67, 76,
                65, 73, 77, 95, 68, 69, 70, 47, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58, 116,
                101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115, 122, 107, 103, 84, 109,
                69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 47, 97, 110, 111, 110, 99,
                114, 101, 100, 115, 47, 118, 48, 47, 83, 67, 72, 69, 77, 65, 47, 70, 49, 68, 67,
                108, 97, 70, 69, 122, 105, 51, 116, 47, 49, 46, 48, 46, 48, 47, 100, 101, 102, 97,
                117, 108, 116, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40, 100, 105, 100, 58, 105, 110,
                100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115,
                122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79, 100,
                105, 100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58,
                51, 76, 112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50,
                53, 70, 90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47,
                83, 67, 72, 69, 77, 65, 47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116, 47,
                49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
                67, 76, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 7, 100, 101, 102, 97, 117, 108, 116, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 68, 123, 34, 110,
                34, 58, 34, 55, 55, 57, 46, 46, 46, 51, 57, 55, 34, 44, 34, 114, 99, 116, 120, 116,
                34, 58, 34, 55, 55, 52, 46, 46, 46, 57, 55, 55, 34, 44, 34, 115, 34, 58, 34, 55,
                53, 48, 46, 46, 56, 57, 51, 34, 44, 34, 122, 34, 58, 34, 54, 51, 50, 46, 46, 46,
                48, 48, 53, 34, 125, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0,
            ];
            let parsed_cred_def =
                CredentialDefinitionRegistry::parse_resolve_credential_definition_result(
                    &client, &data,
                )
                .unwrap();
            assert_eq!(
                credential_definition(
                    &DID::new(ISSUER_ID),
                    &SchemaId::new(SCHEMA_ID),
                    Some(CREDENTIAL_DEFINITION_TAG)
                ),
                parsed_cred_def
            );
        }
    }
}
