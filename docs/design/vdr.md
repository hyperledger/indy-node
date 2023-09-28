# VDR Design

**Disclaimer:** popular packages for working with Ethereum network are very close to `indy-sdk`: their provide tide modules for the whole flow execution.
It may be difficult to reuse only particular functions without full integration. 
In the same, time Indy community follows to idea of splitting complex library into components.

> Rust client library to work with Web3, Solidity smart contracts: https://github.com/tomusdrw/rust-web3

## VDR library assumptions

* VDR library firstly will be implemented independently and later integrate into existing indy vdr/sdk/frameworks.
* VDR library will be written in Rust with providing language wrappers.
* VDR library does conversion of legacy `sov/indy` formatted did's and id's into `indy2` format.  
* VDR library does conversion of ledger formatted entities (DID Document, Schema, Credential Definition) into specifications compatible format.
* VDR library does only basic validation within request builders.
* VDR library does only Ethereum base account signing of transactions.
* VDR library request builders are tide to the network.
* VDR library will work with RPC Node over HTTP.

## Client

```rust
/// Create Indy2.0 client interacting with ledger
///
/// #Params
///  param: chain_id: u64 - chain id of network (chain ID is part of the transaction signing process to protect against transaction replay attack)
///  param: node_address: string - RPC node endpoint
///  param: contract_specs: Vec<ContractSpec> - specifications for contracts  deployed on the networl
///  param: signer: Option<Signer> - transactions signer. Need to be provided for usage of single-step functions. 
/// 
/// #Returns
///  client - client to use for building and sending transactions
fn indy_vdr_create_client(
    chain_id: String,
    node_address: String,
    contract_specs: Vec<ContractSpec>,
    signer: Option<Signer>
) -> Client {
    unimpltemented!()
}

struct ContractSpec {
    name: String, // name of the contract
    address: String, // address of deployed contract
    abi_path: String, // path to JSON file containing contract's ABI
}

trait Signer {
    fn sign(&self, message: &[u8], key: &[u8]) -> TransactionSpec;
}

trait EthClient {}
trait Contract {}

struct Web3Client {
    eth: Web3<Http>
}

impl EthClient for Web3Client {}

struct Web3Contract {
    contract: Contract<Http>
}
impl Contract for Web3Client {}

struct Client {
    client: EthClient, // ethereum client library
    contracts: HashMap<String, Contract>, // list of contract instances
    signer: Signer // transaction signer (wallet)
}

/// Ping Ledger.
///   
/// #Params
///  param: client: Client - Ledger client
/// 
/// #Returns
///   status: object - ping status
///
fn indy_vdr_ping(
    client: Client,
) -> StatusResult {
    unimplemented!();
}

struct  StatusResult {
    status: Status
}

enum Status {
    Ok,
    Err(String)
}

/// Submit prepared transaction to the ledger
///     Depending on the transaction type Write/Read eith send_raw or call ethereum method will be used
///   
/// #Params
///  param: client: Client - Ledger client
///  param: transaction: TransactionSpec - spec of transaction to submit
///  param: options: Option<SubmitTransactionOptions> - extra data required for transaction submitting
/// 
/// #Returns
///   result - transaction execution results (receipt or hash or data itself?? - need to clarify)  
///
fn indy_vdr_submit_transaction(
    client: Client,
    transaction: TransactionSpec
    options: Option<SubmitTransactionOptions>
) -> Receipt {
    unimplemented!()
}

struct TransactionSpec {
    type_: TransactionType,
    txn: Transaction
}

enum TransactionType {
    Read,
    Write
}

struct Transaction {

}

struct SubmitTransactionOptions {

}

struct Receipt {
    
}
```

## Contracts/Requests methods

### DID Document

#### Create DID

##### Request builder

```rust
// Probably we do no even need it
struct BuildTxnOptions {

}
```

```rust
/// Prepare transaction executing `DidRegistry.createDid` smart contract method to create a new DID on the Ledger
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_create_did_transaction(
    client: Client,
    from: String,
    did_document: DidDoc,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec {
    unimplemented!();
}
```

##### Single step contract execution

```rust
/// Single step function executing DidRegistry.createDid smart contract method to publish a new DID Document
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_create_did(
    client: LedgerClient,
    from: String,
    did_document: DidDocument,
    options: Option<BuildTxnOptions>,
) -> Receipt; 
```

#### Update DID

##### Request builder

```rust
/// Prepare transaction executing `DidRegistry.updateDid` smart contract method to update an existing DID Document
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_update_did_transaction(
    client: Client,
    from: String,
    did_document: DidDoc,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing DidRegistry.updateDid smart contract method to publish DID Document
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_update_did(
    client: LedgerClient,
    from: String,
    did_document: DidDocument,
    options: Option<ResolveDidOptions>,
) -> Receipt; 
```

#### Deactivate DID

##### Request builder

```rust
/// Prepare transaction executing `DidRegistry.deactivateDid` smart contract method to deactivate an existing DID
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did: string - did to deactivate
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_deactivate_did_transaction(
    client: Client,
    from: String,
    did: String,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing DidRegistry.deactivateDid smart contract method to publish DID Document
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: did: string - did to activate
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_deactivate_did(
    client: LedgerClient,
    from: String,
    did: String,
    options: Option<ResolveDidOptions>,
) -> Receipt; 
```

#### Resolve DID

##### Request builder

```rust
/// Prepare transaction executing `DidRegistry.resolveDid` smart contract method to resolve a DID
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: did - DID to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_resolve_did_transaction(
    client: Client,
    did: String,
    options: Option<BuildTransactionOptions>,
) -> TransactionSpec;
```

```rust
/// Parse response for of `DidRegistry.resolveDid` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_parse_resolve_did_response(
    client: Client,
    response: bytes,
) -> DidDocumentWithMeta;
```

##### Single step contract execution

```rust
/// Single step function executing DidRegistry.resolveDid smart contract method to resolve DID Document with metadata
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: did - DID to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   did_document_with_meta - resolved DID Document
fn indy_vdr_resolve_did(
    client: LedgerClient,
    did: String,
    options: Option<ResolveDidOptions>,
) -> DidDocumentWithMeta; 
```

```rust
/// Single step function executing dereferencing DID-URL and DidRegistry.resolveDid smart contract method to resolve DID Document with metadata
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: did - DID-URL to derefence
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   did_document_with_meta - resolved DID Document
fn indy_vdr_dereference_did(
    client: LedgerClient,
    did_url: String,
    options: Option<ResolveDidOptions>,
) -> DidDocumentWithMeta; 
```

### Schema

#### Create Schema

##### Request builder

```rust
/// Prepare transaction executing SchemaRegistry.createSchema smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: schema - Schema object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:schema
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_create_schema_transaction(
    client: Client,
    from: String,
    schema: Schema,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing SchemaRegistry.createSchema smart contract method to publish Schema
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: schema - Schema object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:schema
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_create_schema(
    client: LedgerClient,
    from: String,
    schema: Schema,
    options: Option<ResolveDidOptions>,
) -> Receipt; 
```

#### Resolve Schema

##### Request builder

```rust
/// Prepare transaction executing `SchemaRegistry.resolveSchema` smart contract method 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: id - id of Schema to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_resolve_schema_transaction(
    client: Client,
    id: String,
    options: Option<BuildTransactionOptions>,
) -> TransactionSpec;
```

```rust
/// Parse response for of `SchemaRegistry.resolveSchema` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_parse_resolve_schema_response(
    client: Client,
    response: bytes,
) -> SchemaWithMeta;
```

##### Single step contract execution

```rust
/// Single step function executing SchemaRegistry.resolveSchema smart contract method to resolve Schema
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: id - id of Schema to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   schema_with_meta - resolved Schema
fn indy_vdr_resolve_schema(
    client: LedgerClient,
    id: String,
    options: Option<ResolveDidOptions>,
) -> SchemaWithMeta; 
```

### Credential Definition

#### Create Credential Definition

##### Request builder

```rust
/// Prepare transaction executing CredentialDefinitionRegistry.createCredentialDefinition smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: cred_def - Credential Definition object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:credential-definition 
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_create_schema_transaction(
    client: Client,
    from: String,
    cred_def: CredentialDefinition,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing CredentialDefinitionRegistry.createCredentialDefinition smart contract method to piblish Credential Definition
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: cred_def - Credential Definition object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:credential-definition 
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_create_credential_definition(
    client: LedgerClient,
    from: String,
    cred_def: CredentialDefinition,
    options: Option<BuildTxnOptions>,
) -> Receipt;
```

#### Resolve Credential DefinitionCredential Definition

##### Request builder

```rust
/// Prepare transaction executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: id - id of Credential Definition to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_resolve_credential_definition_transaction(
    client: Client,
    id: String,
    options: Option<BuildTransactionOptions>,
) -> TransactionSpec;
```

```rust
/// Parse response for of `CredentialDefinitionRegistry.resolveCredentialDefinition` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_parse_resolve_credential_definition_response(
    client: Client,
    response: bytes,
) -> CredentialDefinitionWithMeta;
```

##### Single step contract execution

```rust
/// Single step function executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract method to resolve Credential Definition
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: id - id of Credential Definition to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   cred_def_with_meta - resolved Schema
fn indy_vdr_resolve_schema(
    client: LedgerClient,
    id: String,
    options: Option<ResolveDidOptions>,
) -> CredentialDefinitionWithMeta;
```

### Auth

#### Assign role

##### Request builder

```rust
/// Prepare transaction executing RoleControl.assignRole smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: to: string - account address to assign role
///  param: role: string - role to assign
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_assign_role_transaction(
    client: Client,
    from: String,
    to: String,
    role: String,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing RoleControl.assignRole smart contract method to assign account role
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: to: string - account address to assign role
///  param: role: string - role to assign
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_assign_role(
    client: LedgerClient,
    from: String,
    to: String,
    role: String,
    options: Option<ResolveDidOptions>,
) -> Receipt; 
```

#### Revoke role

##### Request builder

```rust
/// Prepare transaction executing RoleControl.revokeRole smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: to: string - account address to assign role
///  param: role: string - role to revoke
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_revoke_role_transaction(
    client: Client,
    from: String,
    to: String,
    role: String,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing RoleControl.revokeRole smart contract method to revoke account role
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: to: string - account address to assign role
///  param: role: string - role to assign
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_revoke_role(
    client: LedgerClient,
    from: String,
    to: String,
    role: String,
    options: Option<BuildTxnOptions>,
) -> Receipt; 
```

#### Get role

##### Request builder

```rust
/// Prepare transaction executing RoleControl.getRole smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: account: string - account address to get role
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_get_role_transaction(
    client: Client,
    account: String,
    options: Option<BuildTransactionOptions>,
) -> TransactionSpec;
```

```rust
/// Parse response for of `RoleControl.getRole` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_parse_get_role_response(
    client: Client,
    response: bytes,
) -> AccountRole;
```

##### Single step contract execution

```rust
/// Single step function executing RoleControl.getRole smart contract method to get current validators
///
/// #Params
///  param: client - Ledger client (Ethereum client - for example web3::Http)
///  param: account: string - account address to get role
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   validators - list of current validators
fn indy_vdr_get_role(
    client: LedgerClient,
    account: String,
    options: Option<ResolveDidOptions>,
) -> ValidatorList;
```

### Validator

#### Add validator

##### Request builder

```rust
/// Prepare transaction executing ValidatorControl.addValidator smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: validator: string - address of valdiator to add
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_add_validator_transaction(
    client: Client,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing ValidatorControl.addValidato smart contract method to add new validator node
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: validator: string - address of valdiator to add
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_add_validator(
    client: LedgerClient,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> Receipt; 
```

#### Remove validator

##### Request builder

```rust
/// Prepare transaction executing ValidatorControl.removeValidator smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: validator: string - address of valdiator to remove
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_remove_validator_transaction(
    client: Client,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

##### Single step contract execution

```rust
/// Single step function executing ValidatorControl.removeValidator smart contract method to remove validator node
///
/// #Params
///  param: client: Client - Ledger client
///  param: from: string - sender account address
///  param: validator: string - address of valdiator to remove
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   receipt - transaction Receipt
fn indy_vdr_remove_validator(
    client: LedgerClient,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> Receipt; 
```

#### Get validators

##### Request builder

```rust
/// Prepare transaction executing ValidatorControl.getValdiators smart contract method
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_get_validators_transaction(
    client: Client,
    options: Option<BuildTransactionOptions>,
) -> TransactionSpec;
```

```rust
/// Parse response for of `ValidatorControl.getValdiators` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_parse_get_validators_response(
    client: Client,
    response: bytes,
) -> ValidatorList;

struct ValidatorList {
    validators: Vec<string>
}
```

##### Single step contract execution

```rust
/// Single step function executing CredentialDefinitionRegistry.getValdiators smart contract method to get current validators
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   validators - list of current validators
fn indy_vdr_get_validators(
    client: LedgerClient,
    options: Option<ResolveDidOptions>,
) -> ValidatorList; 
```

## Transaction Spec methods

```rust
/// Get bytes to sign
///
/// #Params
///  param: transaction: TransactionSpec - preparaed transaction 
///
/// #Returns
///   bytes_to_sign - bytes need to be signed
fn indy_vdr_transaction_spec_get_bytes_to_sign(
    transaction: TransactionSpec,
) -> bytes;

/// Set signature for transaction spec.
///
/// #Params
///  param: transaction: TransactionSpec - preparaed transaction 
///  param: signature: bytes - signature bytes
///
/// #Returns
///   did_document_with_meta - resolved DID Document
fn indy_vdr_transaction_spec_set_signature(
    transaction: TransactionSpec,
    signature: bytes,
);
```

????

## Transaction flow example

### Writes

```
client = indy_vdr_create_client(chain_id, node_address, contracts_path)
did_document = {}
transaction = indy_vdr_build_create_did_transaction(client.contract, from, did_document, options): TransactionSpec
signed_transaction = external_wallet_method_to_secp256k1_sign(transaction.data, private_key)
indy_vdr_submit_transaction(client, signed_transaction)
```

### Reads

```
client = indy_vdr_create_client(chain_id, node_address, contracts_path)
did = ""
transaction = indy_vdr_build_resolve_did_transaction(client.contract, did, options): TransactionSpec
indy_vdr_submit_transaction(client, transaction)
```

## Wallet: Transaction signing

* **Algorithm:** `ECDSA` - elliptic curve digital signature.
    * `recoverable`?  - public key can be recovered from the signature
* **Key Types:** - `Secp256k1`
* Steps:
    * `hash = keccak256.Hash(data)`
    * `signature = Secp256k1.sign(hash).`
    * `hex(signature)`

```rust
/// Create Indy2.0 client
///
/// #Params
///  param: mnemonic - string (Optional) seed used for deterministic account generation 
/// 
/// #Returns
///   wallet - wallet used for signing transactions (web3?)
fn external_wallet_method_to_create_wallet_with_ethr_account(
    mnemonic: Option<String>,
) -> Wallet;

struct Wallet {
    keys: Vec<Key>
}

struct Key {
    type: string,
    public_key: Vec<bytes>,
    private_key: Vec<bytes>
}

/// Sign input message using elliptic curve digital signature algorithm.  
///
/// #Params
///  param: message: bytes - message to sign (hashed message according to EIP-191)
///  param: private_key: bytes - key to use for signing 
/// 
/// #Returns
///   signature: bytes - generated signature
fn external_wallet_method_to_Secp256k1_sign(
    message: bytes,
    private_key: bytes
) -> Signature;
```

## Backward compatibility

### DID creation and resolving

#### Backward compatible way consisting of two steps - Will be done later!

1. Assemble basic DID Document according to the steps [here](https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps).
   > DID Doc will not contain any `service` set. Service will be added by a separate ATTRIB operation.
    * Publish DID Document using `DidRegistry.createDid(didDocument, signatures)`
2. Assemble basic DID Document containing only `id` and `service`.  DID Document itself must be already published using NYM operation.
    * Update existing DID Document using `DidRegistry.updateDid(didDocument, signatures)`

> In fact, it's not really backward compatible as we require passing of additional signature for nym and attrib

```rust
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///   Build a basic DID Document using the provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: client: Ledger client
///  param: from: string - sender account address
///  param: dest: string, verkey, alias, role, diddoc_content, version - same as before. Data to build DID Document.
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_nym_transaction(
    client: Client,
    from: String, 
    dest: String, 
    verkey: String, 
    alias: Option<String>,
    role: Option<String>,
    diddoc_content: Option<String>,
    version: Option<String>,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;

/// Prepare transaction executing `DidRegistry.updateDid` smart contract method 
///   Build a basic DID Document using provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: from: string - sender account address
///  param: target_did, hash, raw, enc - same as before. Data to build DID Document.
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
/// 
/// #Returns
///   transaction: TransactionSpec - prepared transaction object 
fn indy_vdr_build_attrib_transaction(
    client: Client,
    from: String, 
    target_did: String, 
    hash: Option<String>,
    raw: Option<String>,
    enc: Option<String>,
    options: Option<BuildTxnOptions>,
) -> TransactionSpec;
```

> Issue: We cannot build the whole DID Document at ATTRIB step. So we need to allow partial update on DidRegistry.updateDid method.
