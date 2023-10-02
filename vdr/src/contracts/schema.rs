use crate::client::{ContractParam, LedgerClient, Transaction};

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
    ) -> Transaction {
        let contract = client.contract(SchemaRegistry::CONTRACT_NAME);

        let params: Vec<ContractParam> = vec![
            ContractParam::String(id.to_string()),
            ContractParam::Tuple(vec![ContractParam::String(schema.name.to_string())]),
        ];

        let data = contract.encode_input(Self::METHOD_CREATE_SCHEMA, &params);

        Transaction {
            to: contract.address(),
            data,
            ..Default::default()
        }
    }

    pub fn build_resolve_schema_transaction(client: &LedgerClient, did: &str) -> Transaction {
        let contract = client.contract(Self::CONTRACT_NAME);

        let params: Vec<ContractParam> = vec![ContractParam::String(did.into())];
        let data = contract.encode_input(Self::METHOD_RESOLVE_SCHEMA, &params);

        return Transaction {
            to: contract.address(),
            data,
            ..Default::default()
        };
    }

    pub fn parse_resolve_schema_result(client: &LedgerClient, bytes: &[u8]) -> Schema {
        let contract = client.contract(Self::CONTRACT_NAME);
        let tokens = contract.decode_output(Self::METHOD_RESOLVE_SCHEMA, bytes);
        Schema {
            name: tokens[0].to_string(),
        }
    }
}
