// Flow to reproduce:
//
// client = indy_vdr_create_client(node_address, contracts_path)
//
// did_document = {}
// signatures = sign_ed25519(did_document, private_key)
//
// // build only contract data??? or the wholde transaction
// //  if contract data only
// transaction = indy_vdr_build_create_did_transaction(did_document, signatures, options)
// //  if transaction
// transaction = indy_vdr_build_create_did_transaction(client.contract, did_document, signatures, options)
//
// Transaction {
// type: write/read - need signing or not + what method to use send_transaction or call
// data: TransactionData
// }
//
// TransactionData {
// to: Some(self.address), // need to set contract address befor doing ethereum signing. So builders neeed to have access to client??
// data: Bytes(fn_data), // contract parameters
// ..Default::default()
// }
//
// signed_transaction = external_wallet_method_to_sign_ethr_transaction(transaction_data, priv_key_bytes)
// indy_vdr_submit_transaction(client, signed_transaction)

use std::collections::HashMap;
use std::str::FromStr;
use std::thread;
use std::time::Duration;
use web3::api::{Accounts, Eth, Namespace};
use web3::contract::Contract;
use web3::ethabi::{Address, Param, ParamType, Token};
use secp256k1::{All, Message, PublicKey, Secp256k1, SecretKey};
use web3::{ethabi, helpers, signing, Web3};
use web3::contract::tokens::Tokenize;
use web3::signing::{keccak256, Key, Signature, SigningError};
use web3::transports::Http;
use web3::types::{Bytes, CallRequest, H256, RawTransaction, SignedTransaction, Transaction, TransactionParameters};

struct Client {
    network: String,
    client: Web3<Http>,
    contracts: HashMap<String, Contract<Http>>,
}

struct ContractSpec {
    name: String,
    address: String,
    abi_path: String,
}

impl Client {
    fn new(node_address: &str, contract_specs: &Vec<ContractSpec>) -> Client {
        let transport = Http::new(node_address).unwrap();
        let web3 = Web3::new(transport);

        let mut contracts = HashMap::new();
        for contract_spec in contract_specs {
            let abi = std::fs::read(&contract_spec.abi_path).unwrap();

            let contract = Contract::from_json(
                web3.eth(),
                Address::from_str(&contract_spec.address).unwrap(),
                abi.as_slice(),
            ).unwrap();
            contracts.insert(contract_spec.name.clone(), contract);
        }

        return Client {
            network: String::from("sov"),
            client: web3,
            contracts,
        };
    }

    async fn sign_transaction(&self, transaction: TransactionParameters, wallet: &Wallet) -> SignedTransaction {
        return self.client.accounts().sign_transaction(transaction, wallet).await.unwrap();
    }

    async fn submit(&self, transaction: Bytes) -> String {
        let result = self.client.eth().send_raw_transaction(transaction).await.unwrap();
        let hash = helpers::serialize(&result);
        hash.as_str().unwrap().to_string()
    }
}

struct Wallet {
    secp: Secp256k1<All>,
    public_key: PublicKey,
    private_key: SecretKey,
}

impl Wallet {
    fn new() -> Wallet {
        let secp = Secp256k1::new();
        let private_key = SecretKey::from_str("8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63").unwrap();
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        return Wallet {
            secp: Secp256k1::new(),
            public_key,
            private_key,
        };
    }

    fn sign_ed(&self) -> Vec<u8> {
        Vec::new()
    }

    fn sign_secp256k1(&self) -> Vec<u8> {
        Vec::new()
    }
}

impl Key for &Wallet {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let message = Message::from_slice(message).map_err(|_| SigningError::InvalidMessage)?;
        let (recovery_id, signature) = self.secp.sign_ecdsa_recoverable(
            &message,
            &self.private_key
        ).serialize_compact();

        let standard_v = recovery_id.to_i32() as u64;
        let v = if let Some(chain_id) = chain_id {
            // When signing with a chain ID, add chain replay protection.
            standard_v + 35 + chain_id * 2
        } else {
            // Otherwise, convert to 'Electrum' notation.
            standard_v + 27
        };
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let message = Message::from_slice(message).map_err(|_| SigningError::InvalidMessage)?;
        let (recovery_id, signature) = self.secp.sign_ecdsa_recoverable(&message, &self.private_key).serialize_compact();

        let v = recovery_id.to_i32() as u64;
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn address(&self) -> web3::types::Address {
        let public_key = self.public_key.serialize_uncompressed();
        let hash = keccak256(&public_key[1..]);
        Address::from_slice(&hash[12..])
    }
}

struct DidDocument {}

impl DidDocument {
    pub fn new() -> DidDocument {
        DidDocument {}
    }
}

struct Signatures {
    kid: String,
    signature: String,
}

impl Signatures {
    fn new(kid: String, signature_bytes: Vec<u8>) -> Signatures {
        Signatures {
            kid,
            signature: bs58::encode(signature_bytes).into_string(),
        }
    }
}

struct Ledger;

struct Schema {
    name: String
}

impl Ledger {
    fn build_create_schema_transaction(client: &Client, id: &str, schema: &Schema) -> TransactionParameters {
        let contract = client.contracts.get("SchemaRegistry").unwrap();

        let params: Vec<Token> = vec![
            Token::String(
                id.to_string()
            ),
            Token::Tuple(
                vec![Token::String(schema.name.to_string())]
            )
        ];

        let function = contract.abi().function("createSchema").unwrap();
        let data = function
            .encode_input(&params)
            .unwrap();

        return TransactionParameters {
            to: Some(contract.address()),
            data: Bytes(data),
            ..Default::default()
        };
    }

    fn build_resolve_schema_transaction(client: &Client, did: &str) -> TransactionParameters {
        let contract = client.contracts.get("SchemaRegistry").unwrap();
        let function = contract.abi().function("resolveSchema").unwrap();

        let data = function
            .encode_input(
                &[Token::String(did.into())]
            ).unwrap();

        return TransactionParameters {
            to: Some(contract.address()),
            data: Bytes(data),
            ..Default::default()
        };
    }

    fn parse_resolve_schema_result(client: &Client, bytes: &[u8]) -> Vec<Token> {
        let contract = client.contracts.get("SchemaRegistry").unwrap();

        let function = contract.abi().function("resolveSchema").unwrap();

        let data = function.decode_output(bytes).unwrap();

        data
    }

}

#[tokio::main]
async fn main() -> web3::Result<()> {
    let client = Client::new("http://127.0.0.1:8545", &vec![
        ContractSpec {
            name: "SchemaRegistry".to_string(),
            address: "0x0000000000000000000000000000000000005555".to_string(),
            abi_path: "/Users/artem/indy-ledger/smart_contracts/artifacts/contracts/cl/SchemaRegistry.sol/spec.json".to_string(),
        }
    ]);
    let wallet = Wallet::new();

    /// write
    /// sign and send
    /// 1. build
    let id = "did:test:2:3:2";
    let schema = Schema {name: "test".to_string()};
    let transaction = Ledger::build_create_schema_transaction(&client, id, &schema);

    /// 2. sign
    let signed_transaction = client.sign_transaction(transaction, &wallet).await;

    /// 3. submit
    let result = client.submit(signed_transaction.raw_transaction).await;
    println!("result {:?}", result);

    /// 4. parse?

    thread::sleep(Duration::from_millis(4000));

    /// read
    /// call
    /// 1. build
    let transaction = Ledger::build_resolve_schema_transaction(&client, id);
    let request = CallRequest::builder()
        .to(transaction.to.unwrap())
        .data(transaction.data)
        .build();
    /// 2. submit
    let result = client.client.eth().call(request, None).await.unwrap();
    /// 3. parse
    println!("result {:?}", Ledger::parse_resolve_schema_result(&client, &result.0));

    Ok(())
}
