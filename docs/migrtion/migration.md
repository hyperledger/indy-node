# Indy migration

This document contains a plan of attack for migration of customers using Indy/Sovrin ledgers to Indy 2.

## Ledger migration

All Issuers need to run migration by itself to move their data (DID Document, Schema, Credential Definition) to Besu ledger.

## Step by step Indy based applications migration flow

This section provides example steps demonstrating the process of migration for applications using Indy ledger to Besu Ledger.
The parties involved into the flow: 
* Trustee - publish Issuer DID on the Ledger
  * Write data to Ledger
* Issuer - publish DID, Schema, and Credential Definition on the Ledger + Issue Credential for a Holder
  * Write data to Ledger
* Holder - accept Credential and share Proof
  * Read data from the Ledger
* Verifier - request Proof from a Holder
    * Read data from the Ledger

### Before migration

At this point, all parties acts as usual and use Indy Ledger as a verifiable data registry.

> Consider that these steps happened some time at the past before the decision to migrate from Indy to Besu ledger.

2. Issuer setup (DID Document, Schema, Credential Definition):
    1. All parties create an indy wallet and uses some Indy Ledger client
    2. Trustee publish Issuer's DID to Indy Ledger using NYM transaction
       ```
       {
            "did": "KWdimUkZrdHURBkQsWv12r",
            "verkey": "B6AfDurBrLF2F7D17RyWjkBx4JT55W9CtuU8wZiXHv1K",
       }
       ```
    3. Issuer publish Service Endpoint to Indy Ledger using ATTRIB
        > According to [indy did method specification](https://hyperledger.github.io/indy-did-method/) data published as NYM and ATTRIB transactions should be used to construct DID Document 
    4. Issuer create and publish Credential Schema to Indy Ledger using SCHEMA
        ```
        {
            "ver":"1.0",
            "id":"KWdimUkZrdHURBkQsWv12r:2:test_credential:1.0.0",
            "name":"test_credential",
            "version":"1.0.0",
            "attrNames":["first_name","last_name"]
        }
        ```
    5. Issuer create and publish Credential Definition to Indy Ledger using CLAIM_DEF
        ```
        {
            "ver":"1.0",
            "id":"KWdimUkZrdHURBkQsWv12r:3:CL:99089:default",
            "schemaId":"99089",
            "type":"CL",
            "tag":"default",
            "value":{...}
        }
        ```
4. Credential issuance
    1. Issuer create Credential Offer
    2. Holder accept Credential Offer:
        1. Resolve Schema from Indy Ledger using GET_SCHEMA request
        2. Resolve Credential Definition from Indy Ledger using GET_CLAIM_DEF request
        3. Create Credential Offer
    3. Issuer sign Credential
    4. Holder store Credential
5. Credential verification
    1. Verifier create Proof Request
    2. Holder accept Proof Request and create Proof
    3. Verifier verify Proof
        1. Resolve Schemas from Indy Ledger using GET_SCHEMA request
        2. Resolve Credential Definitions from Indy Ledger using GET_CLAIM_DEF request
        3. Verify Proof

### Migration

At some point company managing (Issuer,Holder,Verifier) decide to migrate from Indy to Besu Ledger. 

In order to do that, their Issuer's applications need to publish their data to Besu Ledger.
Issuer need to run migration tool manually (on the machine containing Indy Wallet storing Credential Definitions) which migrate data.

* Issuer: 
  * All issuer applications need run migration tool manually (on the machine containing Indy Wallet with Keys and Credential Definitions) in order to move data to Besu Ledger properly. The migration process consist of multiple steps which will be described later.  
  * After the data migration, issuer services should issue new credentials using Besu ledger. 
* Holder: 
  * Holder applications can keep stored credentials as is. There is no need to run migration for credentials which already stored in the wallet. 
  * Holder applications should start using Besu ledger to resolve Schemas and Credential Definition once Issuer completed migration.
* Verifier:
  * Verifier applications should start using Besu ledger to resolve Schemas and Credential Definition once Issuer completed migration.
  * Verifier applications should keep using old styled restriction in order to request credentials which were received before the migration.    

> * Question: Should it be an extra library working with both ledger or application should combine usage of indy and besu clients? 
> * Besu vdr can provide a feature module including migration helpers.
> * Applications still need to use indy client and besu client.

1. Wallet and Client setup
   1. All applications need to integrate Besu vdr library
   ```
   let signer = BasicSigner::new();
   let client = LedgerClient::new(CHAIN_ID, NODE_ADDRESS, contracts, signer);
   ```
      * `CHAIN_ID` - chain id of network (chain ID is part of the transaction signing process to protect against transaction replay attack)
      * `NODE_ADDRESS` - an address of node to connect for sending transactions
      * `contracts` - specifications for contracts deployed on the network
      * `signer` - transactions signer
2. DID ownership moving to Besu Ledger:
    1. Issuer create Ed25518 key (with seed) in the Besu wallet
    2. Issuer create a new Secp256k1 keypair in Besu wallet
    3. Issuer publish Secp256k1 key to Indy ledger using ATTRIB transaction: `{ "besu": { "key": secp256k1_key } }`
       * Now Besu Secp256k1 key is associated with the Issuer DID which is published on the Indy Ledger. 
       * ATTRIB transaction is signed with Ed25518 key. No signature request for `secp256k1_key`. 
3. Issuer build DID Document which will include:
    * DID - fully qualified form should be used: `did:besu:network:<did_value>` of DID which was published as NYM transaction to Indy Ledger
    * Two Verification Methods must be included:
        * `Ed25519VerificationKey2018` key published as NYM transaction to Indy Ledger
           * Key must be represented in multibase as base58 form was deprecated
        * `EcdsaSecp256k1VerificationKey2019` key published as ATTRIB transaction to Indy Ledger
           * Key must be represented in multibase
           * This key will be used in future to sign transactions sending to Besu ledger
             * Transaction signature proves ownership of the key
             * Besu account will be derived from the public key part
    * Two corresponding authentication methods must be included.
    * Service including endpoint which was published as ATTRIB transaction to Indy Ledger
4. Issuer publish DID Document to Besu ledger:
    ```
     let did_doc = build_did_doc(&issuer.did, &issuer.edkey, &issuer.secpkey, &issuer.service);
     let receipt = DidRegistry::create_did(&client, &did_document).await
    ```
    * Transaction is signed using Secp256k1 key `EcdsaSecp256k1VerificationKey2019`. 
       * This key is also included into Did Document associated with DID.
       * Transaction level signature validated by the ledger that proves key ownership.
    * `Ed25519VerificationKey2018` - Besu ledger will not require signature for proving ownership this key.
      * key just stored as part of DID Document and is not validated
      * potentially, we can add verification through the passing an additional signature 
    ```
    { 
        context: "https://www.w3.org/ns/did/v1", 
        id: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r", 
        controller: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r", 
        verificationMethod: [
            { 
                id: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r:KEY-1", 
                type: Ed25519VerificationKey2018, 
                controller: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r",
                publicKeyMultibase: "zH3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
            }, 
            {
                id: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r:KEY-2", 
                type: EcdsaSecp256k1VerificationKey2019, 
                controller: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r", 
                publicKeyMultibase: "zNaqS2qSLZTJcuKLvFAoBSeRFXeivDfyoUqvSs8DQ4ajydz4KbUvT6vdJyz8i9gJEqGjFkCN27niZhoAbQLgk3imn
            }
        ], 
        authentication: [
            "did:indy:testnet:KWdimUkZrdHURBkQsWv12r:KEY-1", 
            "did:indy:testnet:KWdimUkZrdHURBkQsWv12r:KEY-2"
        ], 
        assertionMethod: [], 
        capabilityInvocation: [], 
        capabilityDelegation: [], 
        keyAgreement: [], 
        service: [
            { 
                id: "#inline-1", 
                type: "DIDCommService", 
                serviceEndpoint: "127.0.0.1:5555" 
            }
       ]
    }
    ```
5. Issuer converts Indy styled Schema into new style (anoncreds cpec) and publish it to Besu ledger.
    ```
    let schema = Schema::from_indy_format(&indy_schema);
    let receipt = SchemaRegistry::create_schema(client, &issuer.account, &schema).await
    ```
   * Migration tool will provide a helper method to convert Schema.
   ```
   { 
       id: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r/anoncreds/v0/SCHEMA/test_credential/1.0.0", 
       issuerId: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r", 
       name: "test_credential", 
       version: "1.0.0", 
       attrNames: ["first_name", "last_name"] 
   }
   ```
6. Issuer converts Indy styled Credential Definition into new style (anoncreds cpec) and publish it to Besu Ledger
    ```
    let mut cred_def = CredentialDefinition::from_indy_format(&indy_cred_def);
    cred_def.schema_id = schema.id;
    let receipt = CredentialDefinitionRegistry::create_credential_definition(&client, &issuer.account, &cred_def).await
    ```
    * Migration tool will provide a helper method to convert Credential Definition.
    * Credential Definition ID must include schema seq for achieving backward-compatibility
    * Same time `schemaId` field must contain actual id of schema published to Besu Ledger
   ```
   { 
       id: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r/anoncreds/v0/CLAIM_DEF/99089/default", 
       issuerId: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r", 
       schemaId: "did:indy:testnet:KWdimUkZrdHURBkQsWv12r/anoncreds/v0/SCHEMA/test_credential/1.0.0", 
       credDefType: "CL", 
       tag: "default", 
       value: "{...}"
   }
   ```

### After Migration

All parties switch to use Besu Ledger as verifiable data registry.

Now credential issuance and credential verification flow can run as before but with usage of another vdr library.

1. Credential verification
    1. Verifier create Proof Request
    2. Holder accept Proof Request and create Proof
        1. Holder resolve Schema from Besu Ledger (VDR converts indy schema id representation into Besu form)
           ```
           let schema_id = SchemaId::from_indy_format(&indy_schema_id);
           let schema = SchemaRegistry::resolve_schema(&client, &schema_id).await
           ``` 
           * Migration tool will provide helper to convert old style indy schema id into new format
        2. Holder resolve Credential Definition from Besu Ledger (VDR converts indy cred definition id representation into Besu form)
           ```
           let cred_def_id = CredentialDefinitionId::from_indy_format(cred_def_id);
           let cred_def = CredentialDefinitionRegistry::resolve_credential_definition(&client, id).await
           ``` 
            * Migration tool will provide helper to convert old style indy credential definition id into new format
        3. Create Proof
    3. Verifier verify Proof
        1. Holder resolve Schema from Besu Ledger (VDR converts indy schema id representation into Besu form)
           ```
           let schema_id = SchemaId::from_indy_format(&indy_schema_id);
           let schema = SchemaRegistry::resolve_schema(&client, &schema_id).await
           ``` 
           * Schema id must be converted as well because proof will contain old style ids 
        2. Holder resolve Credential Definition from Besu Ledger (VDR converts indy cred definition id representation into Besu form)
           ```
           let cred_def_id = CredentialDefinitionId::from_indy_format(cred_def_id);
           let cred_def = CredentialDefinitionRegistry::resolve_credential_definition(&client, id).await
           ``` 
        3. Verify proof
2. Credential Issuance goes as before but another ledger is used as a verifiable data registry.


## VDR Backward compatibility

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
