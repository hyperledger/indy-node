use crate::{
    client::{ContractParam, LedgerClient, Transaction, TransactionSpec, TransactionType},
    error::{VdrError, VdrResult},
};
use web3::helpers;

pub struct SchemaRegistry;

#[derive(Debug)]
pub struct Schema {
    pub name: String,
}

impl SchemaRegistry {
    const CONTRACT_NAME: &'static str = "SchemaRegistry";
    const METHOD_CREATE_SCHEMA: &'static str = "createSchema";
    const METHOD_RESOLVE_SCHEMA: &'static str = "resolveSchema";

    pub fn build_create_schema_transaction(
        client: &LedgerClient,
        id: &str,
        schema: &Schema,
    ) -> VdrResult<TransactionSpec> {
        let contract = client.contract(SchemaRegistry::CONTRACT_NAME)?;

        let params: Vec<ContractParam> = vec![
            ContractParam::String(id.to_string()),
            ContractParam::Tuple(vec![ContractParam::String(schema.name.to_string())]),
        ];

        let data = contract.encode_input(Self::METHOD_CREATE_SCHEMA, &params)?;

        let transaction = Transaction {
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
        let values = contract.decode_output(Self::METHOD_RESOLVE_SCHEMA, bytes)?;
        Ok(Schema {
            name: values[0].to_string(),
        })
    }

    pub async fn create_schema(
        client: &LedgerClient,
        id: &str,
        schema: &Schema,
    ) -> VdrResult<String> {
        let mut transaction_spec = Self::build_create_schema_transaction(client, id, schema)?;
        let signed_transaction = client.sign_transaction(&transaction_spec).await?;
        transaction_spec.set_signature(signed_transaction);
        let result = client.submit_transaction(&transaction_spec).await?;
        let hash = helpers::serialize(&result);
        Ok(hash.as_str().ok_or(VdrError::Unexpected)?.to_string())
    }

    pub async fn resolve_schema(client: &LedgerClient, id: &str) -> VdrResult<Schema> {
        let mut transaction_spec = Self::build_resolve_schema_transaction(client, id)?;
        let result = client.submit_transaction(&transaction_spec).await?;
        Self::parse_resolve_schema_result(client, &result)
    }
}
