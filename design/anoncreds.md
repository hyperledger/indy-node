# Anoncreds Design
Here you can find the requirements and design for Anoncreds workflow (including revocation).

* [Anoncreds Link](#anoncreds-links)
* [Requirements](#requirements)
* [Changes in Anoncreds Protocol](#changes-in-anoncreds-protocol)
* [Referencing Schema and CredDef in Credentials and Proofs](#referencing-schema-and-creddef-in-credentials-and-proofs)
* [How Prover and Verifier get keys for Credentials and Proofs](#how-prover-and-verifier-get-keys-for-credentials-and-proofs)
* [Timestamp Support in State](#timestamp-support-in-state)
* [SCHEMA](#schema)
* [CRED_DEF](#cred_def)
* [REVOC_DEF](#revoc_def)
* [REVOC_REG](#revoc_reg)

### Anoncreds Links

Anoncreds protocol links:
- [Anoncreds Sequence Diagram](https://github.com/hyperledger/indy-sdk/blob/master/doc/libindy-anoncreds.svg)
- [Anoncreds Protocol Math](https://github.com/hyperledger/indy-crypto/blob/master/libindy-crypto/docs/AnonCred.pdf)
- [Anoncreds Protocol Crypto API](https://github.com/hyperledger/indy-crypto/blob/master/libindy-crypto/docs/anoncreds-design.md)

### Requirements
1. Creation of Schemas:
    1. Schema Issuer needs to be able to create multiple schemas by the same issuer DID.
    1. Schema Issuer needs to be able to evolve existing schema adding new attributes.
    1. We need to keep reputation for Schema's Issuer DID.
    1. We should not have any semver assumptions for Schema's version by the Ledger.
1. Creation of Cred Def:
    1. CredDef Issuer may not be the same as Schema issuer.
    1. CredDef Issuer needs to be able to create multiple CredDefs by the same issuer DID.
    1. CredDef Issuer needs to be able to create multiple CredDefs for the same Schema by the same issuer DID.
    1. We need to keep reputation for CredDef's Issuer DID.
1. Creation of Revocation entities (Def and Registry):
    1. RevocDef Issuer may not be the same as Schema Issuer and CredDef issuer. 
    1. RevocDef Issuer needs to be able to create multiple RevocDefs for the same issuer DID.
    1. RevocDef Issuer needs to be able to create multiple RevocDef for the same CredDef by the same issuer DID.
    1. We need to keep reputation for RevocDef's Issuer DID.
1. Referencing Schema/CredDef/RevocDef:
    1. Prover needs to know what CredDef (public keys), Schema and RevocDef 
    were used for issuing the credential.  
    1. Verifier needs to know what CredDef (public keys), Schema and RevocDef 
    were used for issuing the credential from the proof.
1. <b>Keys rotation</b>:
    1. Issuer needs to be able to rotate the keys and issue new credentials with the new keys.
    1. Issuer needs to be able to rotate the keys using the same Issuer DID.
1. <b>Validity of already issued credentials when key is compromised</b>: 
    1. If the Issuer's key is compromised and the issuer suspects that it's compromised 
    from the very beginning, then the Issuer should be able to rotate the key so that all issued credentials
    becomes invalid.
    All new credentials issued after rotation should be verifiable against the new key.
    1. If the Issuer published a key at time A, and at time C he realised that the key was compromised at time B (A < B < C), 
    then the Issuer should be able to rotate the key so that all credentials
    issued before time B can be successfully verified using old key, and
    all credentials issued between B and C becomes invalid.
    All new credentials issued after C should be verifiable against the new key.
    1. The Issuer needs to be able to rotate the keys multiple times. Requirement 5.ii must be true for each key rotation.  
1. <b>Revocation</b>
    1. Verifier needs to be able to Verify that the credential is not revoked at the current time
    (the time when proof request is created).
    1. Verifier needs to be able to Verify that the credential is not revoked at the given time (any time in the past).       
1. Querying
    1. One needs to be able to get all CRED_DEFs created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs with the given name created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs with the given name and version created by the given Issuer DID.
    1. One needs to be able to get all REVOC_DEFs created by the given Issuer DID.
    1. One needs to be able to get all REVOC_DEFs created by the given Issuer DID for the given CRED_DEF.    

### Changes in Anoncreds Protocol

* Each Credential must have a reserved mandatory attribute: `issuanceTime`.
    * It's set by the Issuer to specify the time of Issuance.
    * It's needed to fulfill Requirements 5.
* This attribute can be considered as `m3` special attribute (`m1` is master secret, `m2` is credential context, `m3` is issuance time).
* The `issuanceTime` can be disclosed in each proof.
    * The Verifier should use Predicates (instead of disclosing) for the value of `issuanceTime`. 
    * We do not force disclosing `issuanceTime` (if want to avoid correlation),
but if it's not disclosed and not verified as a Predicate, then there is a chance the the proof verification will fail because 
of key rotations.  
    * If `issuanceTime` is not disclosed, then the latest keys will be used.


### Referencing Schema and CredDef in Credentials and Proofs
* Schema is referenced by unique `SchemaDID`.
    * Created for each new Schema.
    * This is different from Schema Issuer DID (DID used to send `SCHEMA` txn) which can be the same for 
    any number of Schemas.
* CredDef is referenced by unique `CredDefDID`.
    * Created for each new CredDef.
    * This is different from CredDef Issuer DID (DID used to send `CRED_DEF` txn) which can be the same for 
    any number of CredDef.
* RevocDef and RevocReg are referenced by unique `RevocDefDID`.
    * Created for each new RevocDef.
    * Used to update RevocReg.
    * This is different from RevocDef Issuer DID (DID used to send `REVOC_DEF` txn) which can be the same for 
    any number of RevocDef.

      
### How Prover and Verifier get keys for Credentials and Proofs
* Proofs and credentials come with `schemaDID`, `credDefDID`, `revocDefDid`.
* Also there is `issuanceTime` attribute in each credential (which can be disclosed in the proof).
* Prover/Verifier looks up SCHEMA using `GET_SCHEMA(schemaDID)` request to the ledger
* Prover/Verifier looks up CRED_DEF using `GET_CRED_DEF(credDefDID, issuanceTime)` request to the ledger
* Prover/Verifier looks up REVOC_DEF using `GET_REVOC_DEF(revocDefDid, issuanceTime)` request to the ledger
* Prover looks up REVOC_REG to update the witness for the given `timestamp` 
 using `GET_REVOC_REG(revocDefDid, timestamp)` request to the ledger
* Verifies looks up REVOC_REG to get accumulator value for the given `timestamp`  
 using `GET_REVOC_REG(revocDefDid, timestamp)` request to the ledger
* Prover and Verifier should look up REVOC_REG by the same `timestamp` when generating and verifying the proof.

### Timestamp Support in State

We need to have a generic way to get the State at the given time.
- State Trie allows to go to the past, that is given the root hash, get the state with this root.
- We may have a mapping of each State update (timestamp) to the corresponding root.
- We need to find a data structure that can help us to find the nearest state timestamp (to get the root) for the given
time.
- So, we will be able to get the data (state) at the given time.

### SCHEMA

##### SCHEMA txn
```
{
    "data": {
        "did":"GEzcdDLhCpGCYRHW82kjHd",
        "attrNames": ["undergrad","last_name","first_name","birth_date","postgrad","expiry_date"],
        "name":"Degree",
        "version":"1.0",
    },
    
    "reqMetadata": {
        "issuerDid":"L5AD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
`schemaDid` is Schema's DID. It's different from `issuerDid`.

##### Restrictions

* Existing Schema (identified by the Schema `did`) can be modified/changed/evolved.
* Only the `issuerDid` can modify existing Schema (that is we need to keep the ownership). 

##### State

We need to have two records for Schema in State Trie in order to have
1. Simple referencing of Schemas in the protocol (by Schema DID)
1. Requirements 8

Record 1:
* key: `schemaIssuerDid | SchemaMarker | schemaName | schemaVersion | schemaDid` 
* value: aggregated txn data

Record 2:
* key: `schemaDid`
* value: Record 1 key


##### GET_SCHEMA
```
{
    'data': {
        'schemaDid': 'GEzcdDLhCpGCYRHW82kjHd',
    },
...
}
```
1. Lookup State Trie to get `schemaIssuerDid | SchemaMarker |schemaName | schemaVersion | schemaDid` by `schemaDid`
using Record2. 
1. Lookup State Trie to get data by the key found above (Record1).

So, we will have 2 lookups for each request. 

### CRED_DEF

##### CRED_DEF txn
```
{
    "data": {
        "did":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
        "oldKeyTrustTime": {                    (optional)
            "from": "10", 
            "to": "30",
        }
    },
    
    "reqMetadata": {
        "issuerDid":"HHAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
* `did` is CredDef's DID. It's different from `issuerDid`.
* `oldKeyTrustTime` can be set each time the key is rotated and defines
 `the intervals when we still can trust the previous value of the key`.
 This is delta; all intervals are accumulated and appended in the State. 
It is needed to deprecate credentials issued during the time when we suspect
the keys were stolen.
We can not always use revocation to deprecate old credentials, since revocation keys can
be stolen as well.  
 

##### Restrictions

* Existing CredDef (identified by the CredDef `did`) can be modified/changed/evolved.
That is rotation of keys is supported.
* Only the `issuerDid` can modify existing CredDef (that is we need to keep the ownership). 


##### State

We need to have two records for CredDef in State Trie in order to have
1. Simple referencing of CredDef in the protocol (by CredDef DID)
1. Requirements 8

Record 1:
* key: `credDefIssuerDid | CredDefMarker | schemaDid | signatureType | credDefDid` 
* value: aggregated txn data plus `trustTime` as an array (each next `trustTme` is appended).

Record 2:
* key: `credDefDid`
* value: Record 1 key

##### How oldKeyTrustTime works
Let's assume that 
* `key1` was issued at `timeA`
* `key2` was issued at `timeC`, and we suspect that `key1` is stolen at `timeB`
* `key3` was issued at `timeE`, and we suspect that `key2` is stolen at `timeD`

So, we need to use (and return by `GET_CRED_DEF`) the following keys, depending on 
the interval the `issuanceTime` belongs to:
* [A,B] -> key1
* [B,C] -> key2 
* [C,D] -> key2
* [D,E] -> key3
* [E, current] -> key3

So, the Credentials issued at intervals [B,C] and [D,E], that is at intervals
when keys are suspicious, will not be verifiable anymore, because they were issued using key1 (key2),
but the Verifies will use key2 (key3) for verification (as returned by `GET_CRED_DEF`). 

The following txns will be put on Ledger:
1.    
 ```
 "data": {
        "did":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key1},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
    },
```
2.    
 ```
 "data": {
        "did":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key2},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
        "oldKeyTrustTime": {          
            ("from": "A", "to": "B"),
            ("from": "C"),
        }
    },
```
3.    
 ```
 "data": {
        "did":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key3},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
        "oldKeyTrustTime": {          
            ("from": "C", "to": "D"),
            ("from": "E"),
        }
    },
```


The current state (Record1) will look the following:
* key: `HHAD5g65TDQr1PPHHRoiGf|CRED_DEF|GEzcdDLhCpGCYRHW82kjHd|CL|TYzcdDLhCpGCYRHW82kjHd`
* value:
 ```
 ....
 "data": {
        "did":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key3},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
        "oldKeyTrustTime": {          
            ("from": "A", "to": "B"),
            ("from": "C", "to": "D"),
            ("from": "E"),
        }
    },
 ....
```
 
##### GET_CRED_DEF
```
{
    'data': {
        'credDefDid': 'TYzcdDLhCpGCYRHW82kjHd',
        'issuanceTime': 20, (optional)
    },
...
}
```
There is a special logic to get the valid and trusted value of the keys
depending on the issuance time:
1. Lookup State Trie to get `credDefIssuerDid | CredDefMarker | schemaDid | signatureType | credDefDid`  by `credDefDid`
using Record2. 
1. Lookup State Trie to get the current state by the key found above (Record1).
1. If no `issuanceTime` provided, then just return the current value.  
1. Try to find the interval (in `oldKeyTrustTime` array) the `issuanceTime` belongs to.
    * If it's greater than the most right interval, then return the current value.
    * If it belongs to an interval, then get the left value (`from`) of the interval.
    * If it's in between intervals, then get the right interval, and get the left value (`from`)
of this interval.
1. Use generic logic to get the root of the State trie at the time `to` found above. 
1. Lookup State Trie with the found root to find the state at that time (the same way as in Steps 1 and 2)

So, we will have from 2 to 5 lookups for each request. 

Result for the Example above:
* `issuanceTime < A` => [A,B] => state at timeA => key1 (OK)
* `A <= issuanceTime <= B` => [A,B] => state at timeA => key1 (OK)
* `B < issuanceTime < C` => [C,D] => state at timeC => key2 (deprecated credentials)
* `C <= issuanceTime <= D` => [C,D] => state at timeC => key2 (OK)
* `D < issuanceTime < E` => [E,...] => state at timeE => key3 (deprecated credentials)
* `issuanceTime > E` => [E,...] => state at timeE => key3 (OK)


### REVOC_DEF

##### REVOC_DEF txn
```
{
    "data": {
        "did":"ZXzcdDLhCpGCYRHW82kjHd",
        "credDefRef":"GEzcdDLhCpGCYRHW82kjHd",
        "accumKey": {},
        "maxCredNum": 1000000
        "tails": {
            "hash": "<SHA256 hash>",
            "location": "<URL>"
        }
        "oldKeyTrustTime": {                    (optional)
            "from": "10", 
            "to": "30",
        }
    },
    
    "reqMetadata": {
        "issuerDid":"MMAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
* `did` is RevocDef's DID. It's different from `issuerDid`.
* `oldKeyTrustTime` can be set each time the accumulator key is rotated and defines
 `the interval when we still can trust the previous value of the key`. 
It is needed to deprecate credentials issued during the time when we suspect
the keys were stolen.
We can not always use revocation to deprecate old credentials, since revocation keys can
be stolen as well.  
 

##### Restrictions

* Existing RevocDef (identified by the RevocDef `did`) can be modified/changed/evolved.
That is rotation of keys is supported.
* Only the `issuerDid` can modify existing RevocDef (that is we need to keep the ownership). 


##### State

We need to have two records for RevocDef in State Trie in order to have
1. Simple referencing of RevocDef in the protocol (by RevocDef DID)
1. Requirements 8

Record 1:
* key: `revocDefIssuerDid | RevocRefMarker | credDefDid | revocDefDid` 
* value: aggregated txn data plus `trustTime` as an array (each next `trustTme` is appended).

Record 2:
* key: `revocDefDid`
* value: Record 1 key


##### GET_REVOC_DEF
```
{
    'data': {
        'revocDefDid': 'ZXzcdDLhCpGCYRHW82kjHd',
        'issuanceTime': 20, (optional)
    },
...
}
```
The logic is the same as for `GET_CLAIM_DEF` (involving Record1, Record2 and `issuanceTime`).


### REVOC_REG

##### REVOC_REG txn
```
{
    "data": {
        "revocRegDid":"ZXzcdDLhCpGCYRHW82kjHd",
        "type": "<issued by default or not>"
        "accum":"<accum_value>",
        "issued": [], (optional)
        "revoked": [],
    },
    
    "reqMetadata": {
        "issuerDid":"MMAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
* `revocRegDid` must match an existing `REVOC_DEF` with the given DID.
* `type`: issuance by default (`issued` will be empty in this case assuming that everything is already issued)
or issuance by request (`issued` will be fulfilled by newly issued indices).
* `issued`: an array of issued indices (may be absent/empty if the type is "issuance by default"); this is delta; will be accumulated in state.
* `revoked`: an array of revoked indices (delta; will be accumulated in state)

##### Restrictions

* Existing RevocReg (identified by the RevocDef `did`) can be modified/changed/evolved.
* Only the `issuerDid` who created the corresponding `REVOC_DEF` can modify it. 


##### State

* key: `revocDefDid` 
* value: aggregated txn data (aggregated accum_value, issued and revoked arrays)


##### GET_REVOC_REG
```
{
    'data': {
        'revocDefDid': 'ZXzcdDLhCpGCYRHW82kjHd',
        'timestamp': 20,
    },
...
}
```
1. Use generic logic to get the root of the State trie at the time `timestamp`. 
1. Lookup State Trie with the found root to find the state for `revocDefDid`.

