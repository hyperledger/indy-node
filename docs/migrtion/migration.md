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

## Step by step Indy based applications migration flow

Consider that the following parties involved into the flow: Trustee, Issuer, Holder, and Verifier.

### Before migration

Past: All parties use Indy Ledger and run flow as usual.

1. Issuer setup (DID Document, Schema, Credential Definition):
    1. Trustee publish Issuer's DID
    2. Issuer publish Service Endpoint to Indy Ledger
        > According to [indy did method](https://hyperledger.github.io/indy-did-method/) NYM and ATTRIB data construct DID Document 
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
> Probably, we even do not need a separate tool. Indy2-VDR can provide a feature module with helper. Applications will need to use `indy_vdr` and `indy2_vdr`.

1. DID ownership moving to Besu Ledger:
    1. Issuer create Ed25518 key (with seed) in the Besu wallet
    2. Issuer create a new Secp256k1 keypair in Besu wallet
    3. Issuer publish generated Secp256k1 key to Indy ledger using ATTRIB transaction 
       * Besu Ethereum style key associated with the previous Issuer DID in Indy Ledger. 
       * Transaction is signed with Ed25518 key.
2. Issuer build DID Document which will include:
    * DID - fully qualified form: `did:besu:network:<did_value>` of DID which was published as NYM transaction to Indy Ledger
    * Two Verification Methods must be included:
        * `Ed25519VerificationKey2018` key published as NYM transaction to Indy Ledger
           * Key must be represented in multibase
        * `EcdsaSecp256k1VerificationKey2019` key published as ATTRIB transaction to Indy Ledger
           * Key must be represented in multibase
           * This key will be used to sign transactions sending to Besu ledger
    * Two corresponding authentication methods must be included.
    * Service including endpoint which was published as ATTRIB transaction to Indy Ledger
3. Issuer publish DID Document to Besu ledger:
    * Transaction is signed using Secp256k1 key `EcdsaSecp256k1VerificationKey2019`. 
       * This key is also included into Did Document associated with DID.
       * Transaction level signature validated by the ledger that proves key ownership.
    * `Ed25519VerificationKey2018` - Besu ledger will not require signature for proving ownership this key.
      * key just stored as part of DID Document and is not validated
      * potentially, we can add verification through the passing an additional signature 
4. Issuer converts Indy styled Schema into new style (anoncreds cpec) and publish it to Besu ledger.
   * Migration tool will provide a helper method to convert Schema.
5. Issuer converts Indy styled Credential Definition into new style (anoncreds cpec) and publish it to Besu Ledger
    * Migration tool will provide a helper method to convert Credential Definition.
    * Credential Definition ID must include schema seq for achieving backward-compatibility
    * Same time `schemaId` field must contain actual id of schema published to Besu Ledger

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
2. Credential Issuance goes as before but another ledger is used as a verifiable data registry.
