## VDR

### DID Document

#### Create

##### Option 1: Strait creation of fully compatible DID Document.

```
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///
/// #Params
///  param: from - Sender account address
///  param: did_document - DID Document matching to the specification: https://www.w3.org/TR/did-core/
///  param: signatures - list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate signature
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
///         txn: object
///      }
transaction = indy_vdr_build_create_did_transaction(
    from: string,
    did_document: DidDoc,
    signatures: Array<DidDoc>,
    options: Option<BuildTxnOptions>,
): Transaction

signed_transaction = external_web3_method_to_sign_ethr_transaction(
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
///   result - transaction execution result (receipt or data itself??)  
///
receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt
```

##### Option 2: Backward compatible way consisting of two steps

1. Assemble basic DID Document according to the steps [here](https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps).
     > DID Doc will not contain any `service` set. Service will be added by separate ATTRIB operation.
   * Publish DID Document using `DidRegistry.createDid(didDocument, signatures)`
2. Assemble basic DID Document containing only `id` and `service`.  DID Document itself must be already published using NYM operation.
   * Update exising DID Document using `DidRegistry.updateDid(didDocument, signatures)`

```
/// Prepare transaction executing `DidRegistry.createDid` smart contract method 
///   Build basic DID Doucment using provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: from - BREACKING CHANGE? must be ethereum account not a DID as before
///  param: dest, verkey, alias, role, diddoc_content, version - same as before. Data to build DID Document.
///  param: signatures - BREAKING CHANGE? list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate signature
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

signed_transaction = external_web3_method_to_sign_ethr_transaction(
    transaction: Transaction,
    private_key: bytes
): SignedTransaction

receipt = indy_vdr_submit_transaction(
    client: LedgerClient,
    signed_transaction: SignedTransaction
    options: SubmitTransactionOptions
): Receipt

/// Prepare transaction executing `DidRegistry.updateDid` smart contract method 
///   Build basic DID Doucment using provided parameters
///   https://hyperledger.github.io/indy-did-method/#diddoc-assembly-steps
///
/// #Params
///  param: submitter_did - BREACKING CHANGE? must be ethereum account not a DID as before
///  param: target_did, hash, raw, enc - same as before. Data to build DID Document.
///  param: signatures - BREAKING CHANGE? list of signatures to prove DID Document ownership
///         [
///            {
///               kid: string - id of the key used to generate signature
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

signed_transaction = external_web3_method_to_sign_ethr_transaction(
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
/// Single step fucntion executing DidRegistry.resolve smart contract method to resolve DID Document with metadata
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
///               kid: string - id of the key used to generate signature
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

signed_transaction = external_web3_method_to_sign_ethr_transaction(
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
/// Single step fucntion executing SchemaRegistry.resolveSchema smart contract method to resolve Schema
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
///               kid: string - id of the key used to generate signature
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

signed_transaction = external_web3_method_to_sign_ethr_transaction(
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
/// Single step fucntion executing CredentialDefinitionRegistry.resolveCredentialDefinition smart contract method to resolve Credential Definition
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
