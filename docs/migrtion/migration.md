# Indy migration

This document contains a plan of attack for migration of customers using Indy/Sovrin ledgers to Indy 2. 

## Ledger migration

## DR Backward compatibility

* Goal: Plan for getting of backward compatible with [indy-vdr](https://github.com/hyperledger/indy-vdr)
* Reason: smoother libraries' integration into existing applications.
  * Valuable for arise frameworks which are still not ledger agnostic (indy tied) like Aca-py or Aries-vcx. Such frameworks will be able to support Ledger 2.0 after simple migration.

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
