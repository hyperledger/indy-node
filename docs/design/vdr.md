# VDR Design

**Disclaimer:** popular packages for working with Ethereum network are very close to `indy-sdk`: their provide tide modules for the whole flow execution.

## Client

```
/// Create Indy2.0 client
///
/// #Params
///  param: node_address: string - RPC node address
///  contract_specs: Vec<ContractSpec> - specifications for deployed contracts
/// 
/// #Returns
///   client - client to use for sending transactions (web3?)
client = indy_vdr_create_client(
    node_address: string,
    contract_specs: Vec<ContractSpec>,
): Client

struct ContractSpec {
    name: String,
    address: String,
    abi_path: String,
}

struct Client {
    eth_client: EthereumCLient,
    contracts: Map<string, Contract>
}

/// Submit transaction to the ledger
///   
///  param: client - Ledger  client (Ethereum client)
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: signed_transaction - Signed transaction
///  param: options - (Optional) extra data required for transaction submitting
///      { 
///         ?      
///      }
/// 
/// #Returns
///   result - transaction execution results (receipt or data itself??)  
///
receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

## Wallet: Transaction signing

* **Algorithm:** `ECDSA` - elliptic curve digital signature.
    * `recoverable`?  - public key can be recovered from the signature
* **Key Types:** - `Secp256k1`
* Steps:
    * `hash = keccak256.Hash(data)`
    * `signature = Secp256k1.sign(hash).`
    * `hex(signature)`

```
/// Create Indy2.0 client
///
/// #Params
///  param: mnemonic - string (Optional) seed used for deterministic account generation 
/// 
/// #Returns
///   wallet - wallet used for signing transactions (web3?)
wallet = external_wallet_method_to_create_wallet_with_ethr_account(
    mnemonic: Option<string>,
): Wallet

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
signature = external_wallet_method_to_Secp256k1_sign(
    message: bytes,
    private_key: bytes
): Signature
```

### Contracts execution

```
client = indy_vdr_create_client(node_address, contracts_path)

did_document = {}
signatures = sign_ed25519(did_document, private_key)

// build only contract data??? or the wholde transaction
//  if contract data only
    transaction = indy_vdr_build_create_did_transaction(did_document, signatures, options): TransactionSpec
//  if transaction
    transaction = indy_vdr_build_create_did_transaction(client.contract, did_document, signatures, options): TransactionSpec

TransactionSpec {
    // need signing or not ---> call or send_transaction
    type: write/read - need signing or not + what method to use send_transaction or call
    // raw transaction to sign? and send
    data: Transaction
}

Transaction {
    to: Some(self.address), // need to set contract address befor doing ethereum signing. So builders neeed to have access to client??
    data: Bytes(fn_data), // contract parameters
    // rest not important fields 
    ..Default::default()
}

signed_transaction = external_wallet_method_to_Secp256k1_sign(transaction.data, private_key)
indy_vdr_submit_transaction(client, signed_transaction)
```

### DID Document

#### Create

##### Option 1: Strait creation of a fully compatible DID Document.

```
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///
/// #Params
///  param: from - Sender account address   Not needed?
///  param: did_document - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: signatures - list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options - (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///      {
///         contract: string - name of contract or some id??? not an address?
///         data: object - preparaed data required for the contract execution
///      }
transaction = indy_vdr_build_create_did_transaction(
    from: string,
    did_document: DidDoc,
    signatures: Array<DidDoc>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

/// Submit transaction to the ledger
///   
///  param: client - Ledger  client (Ethereum client)
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: signed_transaction - Prepared transaction
///  param: options - (Optional) extra data required for transaction submitting
///      { 
///         ?      
///      }
/// 
/// #Returns
///   result - transaction execution results (receipt or data itself??)  
///
receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

##### Option 2: Backward compatible way consisting of two steps

1. Assemble basic DID Document according to the steps [here](https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps).
   > DID Doc will not contain any `service` set. Service will be added by a separate ATTRIB operation.
    * Publish DID Document using `DidRegistry.createDid(didDocument, signatures)`
2. Assemble basic DID Document containing only `id` and `service`.  DID Document itself must be already published using NYM operation.
    * Update existing DID Document using `DidRegistry.updateDid(didDocument, signatures)`

> In fact, it's not really backward compatible as we require passing of additional signature for nym and attrib  

```
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///   Build a basic DID Document using the provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: from - BREACKING CHANGE? must be Ethereum account not a DID as before
///  param: dest, verkey, alias, role, diddoc_content, version - same as before. Data to build DID Document.
///  param: signatures - BREAKING CHANGE? list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options -  BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_nym_transaction(
    from: string, 
    dest: string, 
    verkey: string, 
    alias: Option<string>,
    role: Option<ROLES>,
    diddoc_content: Option<String>,
    version: Option<string>,
    signatures: Array<DidDoc>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt

/// Prepare transaction executing `DidRegistry.updateDid` smart contract method 
///   Build a basic DID Document using provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: submitter_did - BREACKING CHANGE? must be Ethereum account not a DID as before
///  param: target_did, hash, raw, enc - same as before. Data to build DID Document.
///  param: signatures - BREAKING CHANGE? list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options -  BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_attrib_transaction(
    from: string, 
    target_did: string, 
    hash: Option<string>,
    raw: Option<ROLES>,
    enc: Option<String>,
    signatures: Array<DidDoc>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

> Issue: We cannot build the whole DID Document at ATTRIB step. So we need to allow partial update on DidRegistry.updateDid method.

##### Option 3: Combine NYM and Attrib method into single function

Use single function accepting same parameters as previous two but doing DID Document publishing as single step opertion. 

```
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///
/// #Params
///  param: from - BREACKING CHANGE? must be Ethereum account not a DID as before
///  param: dest, verkey, alias, role, diddoc_content, version - same as before. Data to build DID Document.
///  param: hash, raw, end - Attrib transaction parameters
///  param: signatures - BREAKING CHANGE? list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options -  BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_nym_transaction(
    from: string, 
    dest: string, 
    verkey: string, 
    alias: Option<string>,
    role: Option<ROLES>,
    diddoc_content: Option<String>,
    version: Option<string>,
    hash: Option<string>,
    raw: Option<ROLES>,
    enc: Option<String>,
    signatures: Array<DidDoc>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

##### Option 4: Extra smart contract for LegacyDidRegistry fully supporting previous API 

Create and deploy one more smart contract on top of DidRegistry.
This contract will follow legacy API.
Two steps DidDocument publishing. 

```
contract LegacyDidRegistry is DidRegistry {
    function nym() {}
    function attrib() {}
}
```

#### Resolve

```
/// Prepare transaction executing `DidRegistry.resolve` smart contract method 
///
/// #Params
///  param: from - Optional<account address> BREAKING CHANGE? - submitter account address
///  param: id - DID to resolve
///  param: options -  BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_resolve_did_transaction(
    from: string,
    did: string,
    options: Option<BuildTransactionOptions>,
): Transaction

/// Submit transaction to the ledger
result = indy_vdr_submit_transaction(
    client: LedgerClient,
    transaction: Transaction
    options: SubmitTransactionOptions
): Result
```

```
/// Single step function executing DidRegistry.resolve smart contract method to resolve DID Document with metadata
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: id - DID to resolve
///  param: options - (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   did_document_with_meta - resolved DID Document
///
indy_vdr_resolve_did(
    client: LedgerClient,
    id: string,
    options: Option<ResolveDidOptions>,
): DidDocument 
```

### Schema

#### Create

```
/// Prepare transaction executing SchemaRegistry.createSchema smart contract method
///
/// #Params
///  param: from - BREAKING CHANGE? Sender account address
///  param: schema - Schema object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:schema
///  param: signatures - BREAKING CHANGE? list of signatures to prove Schema Issuer DID ownership?
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options - (Optional) BREAKING CHANGE? extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///      {
///         txn: object
///      }
transaction = indy_vdr_build_create_schema_transaction(
    from: string,
    schema: Schema,
    signatures: Array<Signature>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

#### Resolve

```
/// Prepare transaction executing `SchemaRegistry.resolveSchema` smart contract method 
///
/// #Params
///  param: from - Optional<account address> BREAKING CHANGE? - submitter account address
///  param: id - ID of Schema to resolve
///  param: options - BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_resolve_schema_transaction(
    from: string,
    id: string,
    options: Option<BuildTransactionOptions>,
): Transaction

/// Submit transaction to the ledger
result = indy_vdr_submit_transaction(
    client: LedgerClient,
    transaction: Transaction
    options: SubmitTransactionOptions
): Result
```

```
/// Single step function executing SchemaRegistry.resolveSchema smart contract method to resolve Schema
///
/// #Params
///  param: client - Ledger client (Ethereum client - for example web3::Http)
///  param: id - Id of Schema to resolve
///  param: options - (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   schema - resolved Schema
///
indy_vdr_resolve_schema(
    client: LedgerClient,
    id: string,
    options: Option<ResolveOptions>,
): Schema 
```

### Credential Definition

#### Create

```
/// Prepare transaction executing CredentialDefinitionRegistry.createCredentialDefinition smart contract method
///
/// #Params
///  param: from - BREAKING CHANGE? Sender account address
///  param: credDef - Credential Definition object matching to the specification - https://hyperledger.github.io/anoncreds-spec/#term:credential-definition 
///  param: signatures - BREAKING CHANGE? list of signatures to prove Credential Definition Issuer DID ownership?
///         [
///            {
///               kid: string - id of the key used to generate a signature
///               signature: string - base58 encoded signature 
///            }
///         ]
///  param: options - (Optional)BREAKING CHANGE?  extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///      {
///         txn: object
///      }
transaction = indy_vdr_build_cred_def_transaction(
    from: string,
    credDef: CredentialDefinition,
    signatures: Array<Signature>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_wallet_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

#### Resolve

```
/// Prepare transaction executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract method
///
/// #Params
///  param: from - Optional<account address> BREAKING CHANGE? - submitter account address
///  param: id - Id of Credential Definition to resolve
///  param: options -  BREAKING CHANGE? (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   transaction - prepared transaction object 
///
transaction = indy_vdr_build_resolve_cred_def_transaction(
    from: string,
    id: string,
    options: Option<BuildTransactionOptions>,
): Transaction

/// Submit transaction to the ledger
result = indy_vdr_submit_transaction(
    client: LedgerClient,
    transaction: Transaction
    options: SubmitTransactionOptions
): Result
```

```
/// Single step function executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract method to resolve Credential Definition
///
/// #Params
///  param: client - Ledger  client (Ethereum client - for example web3::Http)
///  param: id - id of Credential Definition to resolve
///  param: options - (Optional) extra data required for transaction preparation
///      { 
///         ?      
///      }
/// 
/// #Returns
///   credentialDefinition - resolved Credential Definition
///
indy_vdr_resolve_credential_definition(
    client: LedgerClient,
    id: string,
    options: Option<ResolveOptions>,
): CredentialDefinition 
```
