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
use web3::api::{Accounts, Eth, Namespace};
use web3::contract::Contract;
use web3::ethabi::{Address, Param, ParamType, Token};
use secp256k1::{PublicKey, Secp256k1, SecretKey};
use web3::{ethabi, signing, Web3};
use web3::contract::tokens::Tokenize;
use web3::ethabi::ParamType::Address;
use web3::signing::{Key, Signature, SigningError};
use web3::transports::Http;
use web3::types::{Bytes, CallRequest, Transaction, TransactionParameters};

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

    fn submit() {}
}

struct Wallet {
    public_key: PublicKey,
    private_key: SecretKey,
}

impl Wallet {
    fn new() -> Wallet {
        let secp = Secp256k1::new();
        let private_key = SecretKey::from_str("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX").unwrap();
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        return Wallet {
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

impl signing::Key for &Wallet {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        todo!()
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        todo!()
    }

    fn address(&self) -> web3::types::Address {
        todo!()
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

impl Ledger {
    fn build_create_did_transaction(client: &Client, did_document: &DidDocument, signatures: &[Signatures]) -> TransactionParameters {
        let contract = client.contracts.get("DidRegistry").unwrap();

        let params: Vec<Token> = vec![];

        let function = contract.abi().function("createDid").unwrap();

        let data = function.encode_input(&params.into_tokens()).unwrap();

        return TransactionParameters {
            to: Some(contract.address()),
            data: Bytes(data),
            ..Default::default()
        };
    }
}

#[tokio::main]
async fn main() -> web3::Result<()> {
    let client = Client::new("http://localhost:8545", &vec![]);
    let wallet = Wallet::new();

    let did_document = DidDocument::new();
    let signature = wallet.sign_ed();
    let signatures = vec![
        Signatures::new(String::from("kid"), signature)
    ];


    /// call
    let request = CallRequest::builder()
        .from(Address::from_str(&contract_spec.address).unwrap())
        .build();
    let result = client.client.eth().call(request, None).await.unwrap();


    /// sign and send
    let transaction = Ledger::build_create_did_transaction(&client, &did_document, &signatures);
    let signed_transaction = client.client.accounts().sign_transaction(transaction, &wallet).await.unwrap();
    let result = client.client.eth().send_raw_transaction(signed_transaction.raw_transaction).await.unwrap();
    let receipt = client.client.eth()
        .transaction_receipt(result)
        .await.unwrap().unwrap();
    println!("receipt {:?}", receipt);

    Ok(())
}
