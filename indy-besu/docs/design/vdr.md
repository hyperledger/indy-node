# VDR Design

**Disclaimer:** popular packages for working with Ethereum network are very close to `indy-sdk`: their provide tide
modules for the whole flow execution. It may be difficult to reuse only particular functions without full integration.
In the same, time Indy community follows to idea of splitting complex library into components.

> Rust client library to work with Web3, Solidity smart contracts: https://github.com/tomusdrw/rust-web3

## VDR library assumptions

* VDR library firstly will be implemented independently and later integrate into existing indy vdr/sdk/frameworks.
* VDR library will be written in Rust with providing language wrappers.
* VDR library does conversion of legacy `sov/indy` formatted did's and id's into `indy2` format.
* VDR library does conversion of ledger formatted entities (DID Document, Schema, Credential Definition) into
  specifications compatible format.
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
///  param: contract_specs: Vec<ContractSpec> - specifications for contracts  deployed on the network
///  param: signer: Option<Signer> - transactions signer. Need to be provided for usage of single-step functions. 
///
/// #Returns
///  client - client to use for building and sending transactions
fn indy_vdr_create_client(
    chain_id: u64,
    node_address: String,
    contract_configs: Vec<ContractConfig>,
    signer: Option<Signer>
) -> LedgerClient {
    unimpltemented!()
}

struct ContractConfig {
    address: String, // address of deployed contract
    spec_path: String, // path to JSON file containing compiled contract's ABI specification
}

trait Signer {
    /// Sign message with the key associated with account
    ///
    /// # Params
    /// - `message` message to sign
    /// - `account` account to use for message signing
    ///
    /// # Returns
    /// recovery ID (for public key recovery) and ECDSA signature
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<(i32, Vec<u8>)>;
}

trait Client {
  /// Sign transaction.
  ///
  /// # Params
  /// - `transaction` prepared transaction to sign
  ///
  /// # Returns
  /// signed transaction object
  async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Transaction>;

  /// Submit signed write transaction to the ledger
  ///
  /// # Params
  /// - `transaction` prepared and signed transaction to submit
  ///
  /// # Returns
  /// hash of a block in which transaction included
  async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;

  /// Submit read transaction to the ledger
  ///
  /// # Params
  /// - `transaction` prepared transaction to submit
  ///
  /// # Returns
  /// result data of transaction execution
  async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>>;

  /// Get the receipt for the given block hash
  ///
  /// # Params
  /// - `hash` hash of a block to get the receipt
  ///
  /// # Returns
  /// receipt as JSON string for the requested block
  async fn get_receipt(&self, hash: &[u8]) -> VdrResult<String>;

  /// Check client connection (passed node is alive and return valid ledger data)
  ///
  /// # Returns
  /// ledger status
  async fn ping(&self) -> VdrResult<PingStatus>;
}

trait Contract {
  /// Get the address of deployed contract
  ///
  /// # Returns
  /// address of the deployed contract. Should be used to execute contract methods
  fn address(&self) -> String;

  /// Encode data required for the execution of a contract method
  ///
  /// # Params
  /// - `method` method to execute
  /// - `params` data to pass/encode for contract execution
  ///
  /// # Returns
  /// encoded data to set into transaction
  fn encode_input(&self, method: &str, params: &[ContractParam]) -> VdrResult<Vec<u8>>;

  /// Decode the value (bytes) returned as the result of the execution of a contract method
  ///
  /// # Params
  /// - `method` method to execute
  /// - `output` data to decode (returned as result of sending call transaction)
  ///
  /// # Returns
  /// contract execution result in decoded form
  fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<ContractOutput>;
}

pub struct LedgerClient {
    chain_id: u64, // network chain id
    client: Box<dyn Client>, // ethereum client library
    contracts: HashMap<String, Box<dyn Contract>>, // contract instances
}

/// Ping Ledger.
///   
/// #Params
///  param: client: LedgerClient - Ledger client
///
/// #Returns
///   status: object - ping status
fn indy_vdr_ping(
    client: LedgerClient,
) -> StatusResult {
    unimplemented!();
}

struct StatusResult {
  status: Status
}

enum Status {
  Ok,
  Err(String)
}

/// Sign transaction
///
/// #Params
///  param: client: LedgerClient - Ledger client
///  param: transaction: Transaction - transaction to sign 
///
/// #Returns
///   signed_transaction - signed transaction
fn indy_vdr_sign_transaction(
    client: LedgerClient,
    transaction: Transaction,
) -> Transaction {
  unimplemented!();
}

/// Submit prepared transaction to the ledger
///     Depending on the transaction type Write/Read eith send_raw or call ethereum method will be used to send transaction
///   
/// #Params
///  param: client: LedgerClient - Ledger client
///  param: transaction: Transaction - transaction to submit
///  param: options: Option<SubmitTransactionOptions> - extra data required for transaction submitting
///
/// #Returns
///   result - transaction execution results (receipt or hash or data itself?? - need to clarify)  
///
fn indy_vdr_submit_transaction(
    client: LedgerClient,
    transaction: Transaction,
    options: Option<SubmitTransactionOptions>
) -> Receipt {
    unimplemented!()
}

struct Transaction {
    chain_id: u64,
    type_: TransactionType,
    from: Option<String>,
    to: String,
    data: Vec<u8>,
    signed: Option<Vec<u8>>,
}

enum TransactionType {
    Read,
    Write
}

struct SubmitTransactionOptions {}

type Receipt = Vec<u8>;
```

## Contracts/Requests methods

### DID Document

#### Create DID

##### Request builder

```rust
// Probably we do no even need it
struct BuildTxnOptions {}
```

```rust
/// Prepare transaction executing `IndyDidRegistry.createDid` smart contract method to create a new DID on the Ledger
///
/// #Params
///  param: client: LedgerClient - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_create_did_transaction(
    client: LedgerClient,
    from: String,
    did_document: DidDoc,
    options: Option<BuildTxnOptions>,
) -> Transaction {
    unimplemented!();
}
```

##### Single step contract execution

```rust
/// Single step function executing `IndyDidRegistry.createDid` smart contract method to publish a new DID Document
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
/// Prepare transaction executing `IndyDidRegistry.updateDid` smart contract method to update an existing DID Document
///
/// #Params
///  param: client: LedgerClient - Ledger client
///  param: from: string - sender account address
///  param: did_document: DidDocument - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_update_did_transaction(
    client: LedgerClient,
    from: String,
    did_document: DidDoc,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing `IndyDidRegistry.updateDid smart` contract method to publish DID Document
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
/// Prepare transaction executing `IndyDidRegistry.deactivateDid` smart contract method to deactivate an existing DID
///
/// #Params
///  param: client: LedgerClient - Ledger client
///  param: from: string - sender account address
///  param: did: string - did to deactivate
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_deactivate_did_transaction(
    client: LedgerClient,
    from: String,
    did: String,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing `IndyDidRegistry.deactivateDid` smart contract method to publish DID Document
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
/// Prepare transaction executing `IndyDidRegistry.resolveDid` smart contract method to resolve a DID
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: did - DID to resolve
///  param: options: Option<BuildTxnOptions> - (Optional) extra data required for transaction preparation
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_resolve_did_transaction(
    client: LedgerClient,
    did: String,
    options: Option<BuildTransactionOptions>,
) -> Transaction;
```

```rust
/// Parse response for of `IndyDidRegistry.resolveDid` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_parse_resolve_did_response(
    client: LedgerClient,
    response: bytes,
) -> DidDocumentWithMeta;
```

##### Single step contract execution

```rust
/// Single step function executing `IndyDidRegistry.resolveDid` smart contract method to resolve DID Document with metadata
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
/// Single step function executing dereferencing DID-URL and `IndyDidRegistry.resolveDid` smart contract method to resolve DID Document with metadata
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_create_schema_transaction(
    client: LedgerClient,
    from: String,
    schema: Schema,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing SchemaRegistry.createSchema smart contract method to publish Schema
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_resolve_schema_transaction(
    client: LedgerClient,
    id: String,
    options: Option<BuildTransactionOptions>,
) -> Transaction;
```

```rust
/// Parse response for of `SchemaRegistry.resolveSchema` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_parse_resolve_schema_response(
    client: LedgerClient,
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_create_credential_definition_transaction(
    client: LedgerClient,
    from: String,
    cred_def: CredentialDefinition,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing CredentialDefinitionRegistry.createCredentialDefinition smart contract method to piblish Credential Definition
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_resolve_credential_definition_transaction(
    client: LedgerClient,
    id: String,
    options: Option<BuildTransactionOptions>,
) -> Transaction;
```

```rust
/// Parse response for of `CredentialDefinitionRegistry.resolveCredentialDefinition` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_parse_resolve_credential_definition_response(
    client: LedgerClient,
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
fn indy_vdr_resolve_credential_definition(
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_assign_role_transaction(
    client: LedgerClient,
    from: String,
    to: String,
    role: String,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing RoleControl.assignRole smart contract method to assign account role
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_revoke_role_transaction(
    client: LedgerClient,
    from: String,
    to: String,
    role: String,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing RoleControl.revokeRole smart contract method to revoke account role
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_get_role_transaction(
    client: LedgerClient,
    account: String,
    options: Option<BuildTransactionOptions>,
) -> Transaction;
```

```rust
/// Parse response for of `RoleControl.getRole` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_parse_get_role_response(
    client: LedgerClient,
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_add_validator_transaction(
    client: LedgerClient,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing ValidatorControl.addValidato smart contract method to add new validator node
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_remove_validator_transaction(
    client: LedgerClient,
    from: String,
    validator: String,
    options: Option<BuildTxnOptions>,
) -> Transaction;
```

##### Single step contract execution

```rust
/// Single step function executing ValidatorControl.removeValidator smart contract method to remove validator node
///
/// #Params
///  param: client: LedgerClient - Ledger client
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
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_build_get_validators_transaction(
    client: LedgerClient,
    options: Option<BuildTransactionOptions>,
) -> Transaction;
```

```rust
/// Parse response for of `ValidatorControl.getValidators` smart contract 
///
/// #Params
///  param: client: Ledger - client (Ethereum client - for example web3::Http)
///  param: response: bytes - received response bytes
///
/// #Returns
///   transaction: Transaction - prepared transaction object 
fn indy_vdr_parse_get_validators_response(
    client: LedgerClient,
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

## Transaction methods

???
```

## Transaction flow example

### Writes

```
client = indy_vdr_create_client(chain_id, node_address, contracts_path)
did_document = {}
transaction = indy_vdr_build_create_did_transaction(client.contract, from, did_document, options): Transaction
signature = external_wallet_method_to_secp256k1_sign(transaction.data, private_key)
transaction.set_signature(signature)
indy_vdr_submit_transaction(client, transaction)
```

### Reads

```
client = indy_vdr_create_client(chain_id, node_address, contracts_path)
did = ""
transaction = indy_vdr_build_resolve_did_transaction(client.contract, did, options): Transaction
indy_vdr_submit_transaction(client, transaction)
```

## Wallet: Transaction signing

* **Algorithm:** `ECDSA` - elliptic curve digital signature.
    * `recoverable`? - public key can be recovered from the signature
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
    keys: HashMap<String, Key>
}

struct Key {
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
