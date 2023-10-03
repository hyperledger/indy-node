mod client;
mod contracts;
mod error;
mod signer;
mod utils;

#[cfg(test)]
mod tests {
    use crate::{
        client::{ContractSpec, LedgerClient},
        contracts::{Schema, SchemaRegistry},
        signer::Signer,
        utils::sleep,
    };

    #[async_std::test]
    async fn demo_test() -> web3::Result<()> {
        let contract_specs = vec![
            ContractSpec {
                name: "SchemaRegistry".to_string(),
                address: "0x0000000000000000000000000000000000005555".to_string(),
                abi_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/cl/SchemaRegistry.sol/spec.json".to_string(),
            }
        ];
        let signer = Signer::new();
        let client =
            LedgerClient::new("http://127.0.0.1:8545", &contract_specs, Some(signer)).unwrap();

        // write
        let id = "did:test:2:3:4";
        let schema = Schema {
            name: "test".to_string(),
        };
        let mut transaction_spec =
            SchemaRegistry::build_create_schema_transaction(&client, id, &schema).unwrap();
        let signed_transaction = client.sign_transaction(&transaction_spec).await.unwrap();
        transaction_spec.set_signature(signed_transaction);
        let result = client.submit_transaction(&transaction_spec).await.unwrap();
        println!("result {:?}", result);

        sleep(6000);

        // read
        let transaction_spec =
            SchemaRegistry::build_resolve_schema_transaction(&client, id).unwrap();
        let result = client.submit_transaction(&transaction_spec).await.unwrap();
        println!(
            "result {:?}",
            SchemaRegistry::parse_resolve_schema_result(&client, &result).unwrap()
        );

        Ok(())
    }
}
