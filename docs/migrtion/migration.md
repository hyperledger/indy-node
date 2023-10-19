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

## Step by step flow

Consider the following parties involved into the flow: Trustee, Issuer, Holder, Verifier

### Before migration

All parties use Indy Ledger and run flow as usual.

1. Issuer setup (DID Document, Schema, Credential Definition):
    1. Trustee publish Issuer's DID
    2. Issuer publish Service Endpoint to Indy Ledger
    3. Issuer create and publish Credential Schema to Indy Ledger
    4. Issuer create and publish Credential Definition to Indy Ledger
2. Credential issuance
    1. Issuer create Credential Offer
    2. Holder accept Credential Offer:
        1. Resolve Schema from Indy Ledger
        2. Resolve Credential Definition from Indy Ledger
        3. Create Credential Offer
    3. Issuer sign Credential
    4. Holder store Credential
3. Credential verification
    1. Verifier create Proof Request
    2. Holder accept Proof Request and create Proof
    3. Verifier verify Proof
        1. Resolve Schemas from Indy Ledger
        2. Resolve Credential Definitions from Indy Ledger
        3. Verify Proof

### Migration

Issuer run migration tool manually (on the machine containing Indy Wallet storing Credential Definitions) to move data to Besu Ledger.

> Migration tool should be able to work with both ledgers (Indy and Besu)?

1. DID ownership proving:
    1. Issuer create a new Secp256k1 keypair in Besu wallet
    2. Issuer publish generated Secp256k1 key to Indy ledger using ATTRIB transaction (now key associated with the Issuer DID)
    3. Issuer store ed25519 key into Besu wallet
2. Issuer build DID Document which will include:
    * DID - fully qualified form: `did:besu:network:<did_value>` of DID published as NYM transaction to Indy Ledger
    * Two Verification Methods:
        * `Ed25519VerificationKey2018` key published as NYM transaction to Indy Ledger (multibase key form must be used)
        * `EcdsaSecp256k1VerificationKey2019` key published as ATTRIB transaction to Indy Ledger (multibase key form must be used)
            * This key will be used to sign transactions sending to Besu ledger
    * Two corresponding authentication methods
    * Service including endpoint published as ATTRIB transaction to Indy Ledger
3. Issuer publish DID Document to Besu ledger:
4. Issuer converts Indy styled Schema into new style (anoncreds cpec) and publish it to Besu ledger:
5. Issuer converts Indy styled Credential Definition into new style (anoncreds cpec) and publish it to Besu Ledger
    * Credential Definition ID must include schema seq for achieving backward-compatibility
    * same time `schemaId` field must contain actual id of schema published to Besu Ledger

##### Key ownership proving

* EcdsaSecp256k1VerificationKey2019 - Write transactions sending to Besu ledger will be signed using this key.
    * key included into Did Document associated with DID.
    * Transaction level signature proves key ownership.
* Ed25519VerificationKey2018 - Besu ledger will not require signature for proving of this ownership.
    * key just stored as part of DID Document and is not validated

### After Migration

All parties switch to use Besu Ledger.

There is no need to run migration on the Holder side (for previously stored credentials).
Holder and Verifier just can switch to use Besu Ledger for resolving DID Documents, Schemas, and Credential Definitions.

> Question: How to deal with Proof Request restrictions??? Verifier must set restrictions in old ID's style

1. Credential verification
    1. Verifier create Proof Request
    2. Holder accept Proof Request and create Proof
        1. Holder resolve Schema from Besu Ledger (VDR converts indy schema id representation into Besu form)
        2. Holder resolve Credential Definition from Besu Ledger (VDR converts indy cred definition id representation into Besu form)
        3. Create Proof
    3. Verifier verify Proof
        1. Holder resolve Schema from Besu Ledger (VDR converts indy schema id representation into Besu form)
        2. Holder resolve Credential Definition from Besu Ledger (VDR converts indy cred definition id representation into Besu form)
        3. Verify proof
