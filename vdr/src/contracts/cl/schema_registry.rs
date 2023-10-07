use crate::{
    client::{ContractParam, LedgerClient, Transaction, TransactionType},
    contracts::cl::schema::{Schema, SchemaWithMeta},
    error::{VdrError, VdrResult},
};

pub struct SchemaRegistry;

impl SchemaRegistry {
    const CONTRACT_NAME: &'static str = "SchemaRegistry";
    const METHOD_CREATE_SCHEMA: &'static str = "createSchema";
    const METHOD_RESOLVE_SCHEMA: &'static str = "resolveSchema";

    pub fn build_create_schema_transaction(
        client: &LedgerClient,
        from: &str,
        schema: &Schema,
    ) -> VdrResult<Transaction> {
        let contract = client.contract(SchemaRegistry::CONTRACT_NAME)?;

        let params: Vec<ContractParam> = vec![schema.clone().into()];

        let data = contract.encode_input(Self::METHOD_CREATE_SCHEMA, &params)?;

        let transaction = Transaction {
            type_: TransactionType::Write,
            chain_id: client.chain_id(),
            from: Some(from.to_string()),
            to: contract.address(),
            data,
            signed: None,
        };
        Ok(transaction)
    }

    pub fn build_resolve_schema_transaction(
        client: &LedgerClient,
        id: &str,
    ) -> VdrResult<Transaction> {
        let contract = client.contract(Self::CONTRACT_NAME)?;

        let params: Vec<ContractParam> = vec![ContractParam::String(id.into())];
        let data = contract.encode_input(Self::METHOD_RESOLVE_SCHEMA, &params)?;

        let transaction = Transaction {
            type_: TransactionType::Read,
            chain_id: client.chain_id(),
            from: None,
            to: contract.address(),
            data,
            signed: None,
        };
        Ok(transaction)
    }

    pub fn parse_resolve_schema_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<Schema> {
        let contract = client.contract(Self::CONTRACT_NAME)?;
        let output = contract.decode_output(Self::METHOD_RESOLVE_SCHEMA, bytes)?;
        if output.is_empty() {
            return Err(VdrError::Common(
                "Unable to parse Schema: Empty data".to_string(),
            ));
        }

        let schema_data = output.get_tuple(0)?;
        let schema_with_meta = SchemaWithMeta::try_from(schema_data)?;
        Ok(schema_with_meta.schema)
    }

    pub async fn create_schema(
        client: &LedgerClient,
        from: &str,
        schema: &Schema,
    ) -> VdrResult<Vec<u8>> {
        let transaction = Self::build_create_schema_transaction(client, from, schema)?;
        let signed_transaction = client.sign_transaction(&transaction).await?;
        client.submit_transaction(&signed_transaction).await
    }

    pub async fn resolve_schema(client: &LedgerClient, id: &str) -> VdrResult<Schema> {
        let transaction = Self::build_resolve_schema_transaction(client, id)?;
        let result = client.submit_transaction(&transaction).await?;
        Self::parse_resolve_schema_result(client, &result)
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use crate::{
        client::test::{client, ACCOUNT, CHAIN_ID, SCHEMA_REGISTRY_ADDRESS},
        contracts::cl::schema::test::{schema, SCHEMA_NAME},
    };

    const ISSUER_ID: &'static str = "did:indy2:testnet:GNd75u7mFpjX";

    mod build_create_schema_transaction {
        use super::*;

        #[test]
        fn build_create_schema_transaction_test() {
            let client = client();
            let transaction = SchemaRegistry::build_create_schema_transaction(
                &client,
                ACCOUNT,
                &schema(ISSUER_ID, Some(SCHEMA_NAME)),
            )
            .unwrap();
            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
                to: SCHEMA_REGISTRY_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: vec![
                    108, 92, 68, 108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 160, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 1, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 1, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 69, 100, 105,
                    100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 71,
                    78, 100, 55, 53, 117, 55, 109, 70, 112, 106, 88, 47, 97, 110, 111, 110, 99,
                    114, 101, 100, 115, 47, 118, 48, 47, 83, 67, 72, 69, 77, 65, 47, 109, 49, 68,
                    81, 108, 121, 49, 70, 120, 85, 80, 115, 47, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 30, 100, 105, 100, 58, 105, 110, 100, 121, 50, 58, 116, 101, 115, 116, 110,
                    101, 116, 58, 71, 78, 100, 55, 53, 117, 55, 109, 70, 112, 106, 88, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 12, 109, 49, 68, 81, 108, 121, 49, 70, 120, 85, 80, 115, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 49, 46, 48,
                    46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    10, 70, 105, 114, 115, 116, 32, 78, 97, 109, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 76, 97, 115, 116, 32, 78,
                    97, 109, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0,
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
            let client = client();
            let transaction = SchemaRegistry::build_resolve_schema_transaction(
                &client,
                &schema(ISSUER_ID, Some(SCHEMA_NAME)).id,
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
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 69, 100, 105, 100, 58, 105,
                    110, 100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 71, 78, 100, 55,
                    53, 117, 55, 109, 70, 112, 106, 88, 47, 97, 110, 111, 110, 99, 114, 101, 100,
                    115, 47, 118, 48, 47, 83, 67, 72, 69, 77, 65, 47, 109, 49, 68, 81, 108, 121,
                    49, 70, 120, 85, 80, 115, 47, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                ],
                signed: None,
            };
            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_resolve_schema_result {
        use super::*;

        #[test]
        fn parse_resolve_schema_result_test() {
            let client = client();
            let data = vec![
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 101, 32, 238, 99, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 160, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                1, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 1, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 69, 100, 105, 100, 58, 105, 110,
                100, 121, 50, 58, 116, 101, 115, 116, 110, 101, 116, 58, 71, 78, 100, 55, 53, 117,
                55, 109, 70, 112, 106, 88, 47, 97, 110, 111, 110, 99, 114, 101, 100, 115, 47, 118,
                48, 47, 83, 67, 72, 69, 77, 65, 47, 109, 49, 68, 81, 108, 121, 49, 70, 120, 85, 80,
                115, 47, 49, 46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 100, 105, 100, 58, 105, 110, 100, 121, 50,
                58, 116, 101, 115, 116, 110, 101, 116, 58, 71, 78, 100, 55, 53, 117, 55, 109, 70,
                112, 106, 88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 109, 49, 68, 81, 108, 121, 49, 70, 120, 85, 80,
                115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 49,
                46, 48, 46, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 70, 105, 114,
                115, 116, 32, 78, 97, 109, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 9, 76, 97, 115, 116, 32, 78, 97, 109, 101, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ];
            let parsed_schema =
                SchemaRegistry::parse_resolve_schema_result(&client, &data).unwrap();
            assert_eq!(schema(ISSUER_ID, Some(SCHEMA_NAME)), parsed_schema);
        }
    }
}
