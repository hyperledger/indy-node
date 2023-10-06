use crate::{
    client::{ContractParam, LedgerClient, Transaction, TransactionSpec, TransactionType},
    contracts::{cl::schema::Schema, schema::SchemaWithMeta},
    error::{VdrError, VdrResult},
};

pub struct SchemaRegistry;

impl SchemaRegistry {
    const CONTRACT_NAME: &'static str = "SchemaRegistry";
    const METHOD_CREATE_SCHEMA: &'static str = "createSchema";
    const METHOD_RESOLVE_SCHEMA: &'static str = "resolveSchema";

    pub fn build_create_schema_transaction(
        client: &LedgerClient,
        schema: &Schema,
    ) -> VdrResult<TransactionSpec> {
        let contract = client.contract(SchemaRegistry::CONTRACT_NAME)?;

        let params: Vec<ContractParam> = vec![schema.clone().into()];

        let data = contract.encode_input(Self::METHOD_CREATE_SCHEMA, &params)?;

        let transaction = Transaction {
            chain_id: client.chain_id(),
            to: contract.address(),
            data,
            ..Default::default()
        };
        Ok(TransactionSpec {
            transaction_type: TransactionType::Write,
            transaction,
            ..Default::default()
        })
    }

    pub fn build_resolve_schema_transaction(
        client: &LedgerClient,
        id: &str,
    ) -> VdrResult<TransactionSpec> {
        let contract = client.contract(Self::CONTRACT_NAME)?;

        let params: Vec<ContractParam> = vec![ContractParam::String(id.into())];
        let data = contract.encode_input(Self::METHOD_RESOLVE_SCHEMA, &params)?;

        let transaction = Transaction {
            chain_id: client.chain_id(),
            to: contract.address(),
            data,
            ..Default::default()
        };
        Ok(TransactionSpec {
            transaction_type: TransactionType::Read,
            transaction,
            ..Default::default()
        })
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

    pub async fn create_schema(client: &LedgerClient, schema: &Schema) -> VdrResult<Vec<u8>> {
        let mut transaction_spec = Self::build_create_schema_transaction(client, schema)?;
        let signed_transaction = client.sign_transaction(&transaction_spec).await?;
        transaction_spec.set_signature(signed_transaction);
        client.submit_transaction(&transaction_spec).await
    }

    pub async fn resolve_schema(client: &LedgerClient, id: &str) -> VdrResult<Schema> {
        let transaction_spec = Self::build_resolve_schema_transaction(client, id)?;
        let result = client.submit_transaction(&transaction_spec).await?;
        Self::parse_resolve_schema_result(client, &result)
    }
}
