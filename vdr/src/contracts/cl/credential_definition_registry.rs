use crate::{
    client::{
        ContractParam, LedgerClient, Transaction, TransactionBuilder, TransactionParser,
        TransactionType,
    },
    contracts::cl::types::{
        credential_definition::{CredentialDefinition, CredentialDefinitionWithMeta},
        credential_definition_id::CredentialDefinitionId,
    },
    error::VdrResult,
};

pub struct CredentialDefinitionRegistry;

impl CredentialDefinitionRegistry {
    const CONTRACT_NAME: &'static str = "CredentialDefinitionRegistry";
    const METHOD_CREATE_CREDENTIAL_DEFINITION: &'static str = "createCredentialDefinition";
    const METHOD_RESOLVE_CREDENTIAL_DEFINITION: &'static str = "resolveCredentialDefinition";

    pub fn build_create_credential_definition_transaction(
        client: &LedgerClient,
        from: &str,
        credential_definition: &CredentialDefinition,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_CREATE_CREDENTIAL_DEFINITION)
            .add_param(credential_definition.clone().into())
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(&client)
    }

    pub fn build_resolve_credential_definition_transaction(
        client: &LedgerClient,
        id: &CredentialDefinitionId,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION)
            .add_param(ContractParam::String(id.value().into()))
            .set_type(TransactionType::Read)
            .build(&client)
    }

    pub fn parse_resolve_credential_definition_result(
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<CredentialDefinition> {
        TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_CREDENTIAL_DEFINITION)
            .parse::<CredentialDefinitionWithMeta>(&client, bytes)
            .map(|credential_definition_with_meta| {
                credential_definition_with_meta.credential_definition
            })
    }

    pub async fn create_credential_definition(
        client: &LedgerClient,
        from: &str,
        credential_definition: &CredentialDefinition,
    ) -> VdrResult<String> {
        let transaction = Self::build_create_credential_definition_transaction(
            client,
            from,
            credential_definition,
        )?;
        client.sign_and_submit(&transaction).await
    }

    pub async fn resolve_credential_definition(
        client: &LedgerClient,
        id: &CredentialDefinitionId,
    ) -> VdrResult<CredentialDefinition> {
        let transaction = Self::build_resolve_credential_definition_transaction(client, id)?;
        let result = client.submit_transaction(&transaction).await?;
        Self::parse_resolve_credential_definition_result(client, &result)
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
            did::did_doc::test::ISSUER_ID,
        },
        did::DID,
        signer::test::ACCOUNT,
    };

    mod build_create_credential_definition_transaction {
        use super::*;

        #[test]
        fn build_create_credential_definition_transaction_test() {
            let client = client();
            let transaction =
                CredentialDefinitionRegistry::build_create_credential_definition_transaction(
                    &client,
                    ACCOUNT,
                    &credential_definition(
                        &DID::new(ISSUER_ID),
                        &SchemaId::new(SCHEMA_ID),
                        Some(CREDENTIAL_DEFINITION_TAG),
                    ),
                )
                .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
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
            let client = client();
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
            let client = client();
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
