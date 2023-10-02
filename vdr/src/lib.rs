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
        let client = LedgerClient::new("http://127.0.0.1:8545", &vec![
            ContractSpec {
                name: "SchemaRegistry".to_string(),
                address: "0x0000000000000000000000000000000000005555".to_string(),
                abi_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/cl/SchemaRegistry.sol/spec.json".to_string(),
            }
        ]);
        let signer = Signer::new();

        // write
        let id = "did:test:2:3:4";
        let schema = Schema {
            name: "test".to_string(),
        };
        let transaction = SchemaRegistry::build_create_schema_transaction(&client, id, &schema);
        let signed_transaction = client.sign_transaction(transaction, &signer).await;
        let result = client.submit(&signed_transaction).await;
        println!("result {:?}", result);

        sleep(6000);

        // read
        let transaction = SchemaRegistry::build_resolve_schema_transaction(&client, id);
        let result = client.call(&transaction).await;
        println!(
            "result {:?}",
            SchemaRegistry::parse_resolve_schema_result(&client, &result)
        );

        Ok(())
    }
}
