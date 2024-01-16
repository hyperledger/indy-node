use log::{debug, info};

use crate::{
    client::{
        Address, ContractParam, LedgerClient, Transaction, TransactionBuilder, TransactionParser,
        TransactionType,
    },
    contracts::cl::types::{
        schema::{Schema, SchemaWithMeta},
        schema_id::SchemaId,
    },
    error::VdrResult,
};

/// SchemaRegistry contract methods
pub struct SchemaRegistry;

impl SchemaRegistry {
    const CONTRACT_NAME: &'static str = "SchemaRegistry";
    const METHOD_CREATE_SCHEMA: &'static str = "createSchema";
    const METHOD_RESOLVE_SCHEMA: &'static str = "resolveSchema";

    /// Build transaction to execute SchemaRegistry.createSchema contract method to create a new Schema
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `schema` Schema object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:schema
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_create_schema_transaction(
        client: &LedgerClient,
        from: &Address,
        schema: &Schema,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, schema: {:?}",
            Self::METHOD_CREATE_SCHEMA,
            from.value(),
            schema
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_CREATE_SCHEMA)
            .add_param(schema.clone().into())
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_CREATE_SCHEMA,
            transaction
        );

        transaction
    }

    /// Build transaction to execute SchemaRegistry.resolveSchema contract method to retrieve an existing Schema by the given id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `id` id of Schema to resolve
    ///
    /// # Returns
    /// Read transaction to submit
    pub fn build_resolve_schema_transaction(
        client: &LedgerClient,
        id: &SchemaId,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Schema ID: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            id
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_SCHEMA)
            .add_param(ContractParam::String(id.value().into()))
            .set_type(TransactionType::Read)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            transaction
        );

        transaction
    }

    /// Parse the result of execution SchemaRegistry.resolveSchema contract method to receive a Schema associated with the id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `bytes` result bytes returned from the ledger
    ///
    /// # Returns
    /// parsed Schema
    pub fn parse_resolve_schema_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<Schema> {
        debug!(
            "{} result parse has started. Bytes to parse: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            bytes
        );

        let result = TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_RESOLVE_SCHEMA)
            .parse::<SchemaWithMeta>(client, bytes)
            .map(|schema_with_meta| schema_with_meta.schema);

        info!(
            "{} result parse has finished. Result: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            result
        );

        result
    }

    /// Single step function executing SchemaRegistry.createSchema smart contract method to create a new Schema
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `schema` Schema object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:schema
    ///
    /// # Returns
    /// receipt of executed transaction
    pub async fn create_schema(
        client: &LedgerClient,
        from: &Address,
        schema: &Schema,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Sender: {}, Schema: {:?}",
            Self::METHOD_CREATE_SCHEMA,
            from.value(),
            schema
        );

        let transaction = Self::build_create_schema_transaction(client, from, schema)?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_CREATE_SCHEMA,
            receipt
        );

        receipt
    }

    /// Single step function executing SchemaRegistry.resolveSchema smart contract method to resolve Schema for an existing id
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `id` id of Schema to resolve
    ///
    /// # Returns
    /// resolved Schema
    pub async fn resolve_schema(client: &LedgerClient, id: &SchemaId) -> VdrResult<Schema> {
        debug!(
            "{} process has started. SchemaId: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            id
        );

        let transaction = Self::build_resolve_schema_transaction(client, id)?;
        let result = client.submit_transaction(&transaction).await?;
        let parsed_result = Self::parse_resolve_schema_result(client, &result);

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_RESOLVE_SCHEMA,
            parsed_result
        );

        parsed_result
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        client::test::{client, CHAIN_ID, SCHEMA_REGISTRY_ADDRESS},
        contracts::{
            cl::types::schema::test::{schema, SCHEMA_NAME},
            did::types::did_doc::test::ISSUER_ID,
        },
        signer::basic_signer::test::TRUSTEE_ACC,
        utils::init_env_logger,
        DID,
    };

    #[cfg(feature = "ledger_test")]
    pub async fn create_schema(client: &LedgerClient, issuer_id: &DID) -> Schema {
        let schema = schema(issuer_id, None);
        let _receipt = SchemaRegistry::create_schema(&client, &TRUSTEE_ACC, &schema)
            .await
            .unwrap();
        schema
    }

    mod build_create_schema_transaction {
        use super::*;

        #[test]
        fn build_create_schema_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction = SchemaRegistry::build_create_schema_transaction(
                &client,
                &TRUSTEE_ACC,
                &schema(&DID::new(ISSUER_ID), Some(SCHEMA_NAME)),
            )
            .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
                to: SCHEMA_REGISTRY_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: vec![
                    108, 92, 68, 108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 160, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 1, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 1, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79, 100, 105,
                    100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51,
                    76, 112, 106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50,
                    53, 70, 90, 119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48,
                    47, 83, 67, 72, 69, 77, 65, 47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51,
                    116, 47, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 40, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58, 116, 101,
                    115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115, 122, 107, 103, 84, 109, 69,
                    51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 70, 49, 68, 67,
                    108, 97, 70, 69, 122, 105, 51, 116, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 70, 105, 114, 115, 116, 32,
                    78, 97, 109, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 9, 76, 97, 115, 116, 32, 78, 97, 109, 101, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                ],
                signed: None,
            };
            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_resolve_schema_transaction {
        use super::*;

        #[test]
        fn build_resolve_schema_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction = SchemaRegistry::build_resolve_schema_transaction(
                &client,
                &schema(&DID::new(ISSUER_ID), Some(SCHEMA_NAME)).id,
            )
            .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Read,
                from: None,
                to: SCHEMA_REGISTRY_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: vec![
                    189, 127, 197, 235, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79, 100, 105, 100, 58, 105,
                    110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106,
                    115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90,
                    119, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47, 83, 67,
                    72, 69, 77, 65, 47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116, 47, 49,
                    46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                ],
                signed: None,
            };
            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_resolve_schema_result {
        use super::*;
        use crate::DID;

        #[test]
        fn parse_resolve_schema_result_test() {
            init_env_logger();
            let client = client(None);
            let data = vec![
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 101, 39, 237, 175, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 160, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 1, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 1, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79, 100, 105, 100, 58, 105, 110,
                100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112, 106, 115,
                122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90, 119, 47,
                97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118, 48, 47, 83, 67, 72, 69, 77, 65,
                47, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116, 47, 49, 46, 48, 46, 48, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40, 100, 105, 100, 58,
                105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 51, 76, 112,
                106, 115, 122, 107, 103, 84, 109, 69, 51, 113, 84, 104, 103, 101, 50, 53, 70, 90,
                119, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 12, 70, 49, 68, 67, 108, 97, 70, 69, 122, 105, 51, 116, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 70, 105, 114, 115, 116, 32, 78, 97, 109, 101,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 76,
                97, 115, 116, 32, 78, 97, 109, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0,
            ];
            let parsed_schema =
                SchemaRegistry::parse_resolve_schema_result(&client, &data).unwrap();
            assert_eq!(
                schema(&DID::new(ISSUER_ID), Some(SCHEMA_NAME)),
                parsed_schema
            );
        }
    }
}
