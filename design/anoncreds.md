# Anoncreds Design
Here you can find the requirements and design for Anoncreds workflow (including revocation).

* [Anoncreds References](#anoncreds-references)
* [Requirements](#requirements)
* [Referencing Anoncreds Entities](#referencing-anoncreds-entities)
* [SCHEMA](#schema)
* [CRED_DEF](#cred_def)
* [REVOC_REG_DEF](#revoc_reg_def)
* [REVOC_REG_ENTRY](#revoc_reg_entry)
* [Timestamp Support in State](#timestamp-support-in-state)
* [GET_OBJ](#get_obj)
* [Issuer Key Rotation](#issuer-key-rotation)

## Anoncreds References

Anoncreds protocol links:
- [Anoncreds Sequence Diagram](https://github.com/hyperledger/indy-sdk/blob/master/doc/libindy-anoncreds.svg)
- [Anoncreds Protocol Math](https://github.com/hyperledger/indy-crypto/blob/master/libindy-crypto/docs/AnonCred.pdf)
- [Anoncreds Protocol Crypto API](https://github.com/hyperledger/indy-crypto/blob/master/libindy-crypto/docs/anoncreds-design.md)

## Requirements
1. Creation of Schemas:
    1. Schema Author needs to be able to create multiple schemas by the same issuer DID.
    1. Schema Author needs to be able to evolve schemas by adding new attributes (a new Schema with a new name/version 
    can be created). 
    1. No one can modify existing Schemas.
    1. We need to keep reputation for Schema's Issuer DID.
    1. We should not have any semver assumptions for Schema's version by the Ledger.
1. Creation of Cred Def:
    1. CredDef Issuer may not be the same as Schema Author.
    1. CredDef Issuer needs to be able to create multiple CredDefs by the same issuer DID.
    1. CredDef Issuer needs to be able to create multiple CredDefs for the same Schema by the same issuer DID.
    1. We need to keep reputation for CredDef's Issuer DID.
1. Creation of Revocation Registry (Def and Enteries):
    1. RevocReg Issuer may not be the same as Schema Author and CredDef issuer. 
    1. RevocReg Issuer needs to be able to create multiple RevocRegs for the same issuer DID.
    1. RevocReg Issuer needs to be able to create multiple RevocReg for the same CredDef by the same issuer DID.
    1. We need to keep reputation for RevocReg's Issuer DID.
1. Referencing Schema/CredDef/RevocReg:
    1. Prover needs to know what CredDef (public keys), Schema and RevocReg 
    were used for issuing the credential.  
    1. Verifier needs to know what CredDef (public keys), Schema and RevocReg 
    were used for issuing the credential from the proof.
    1. The reference must be compact (a single value).
1. Keys rotation:
    1. Issuer needs to be able to rotate the keys and issue new credentials with the new keys.
    1. Issuer needs to be able to rotate the keys using the same Issuer DID.
    1. Only CredDef's Issuer can modify existing CredDef (that is rotate keys).
1. Validity of already issued credentials when key is compromised: 
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
    1. The Issuer needs to be able to deprecate all credentials created by a rotated key
      and re-issue all existing credentials.
1. Revocation
    1. Verifier needs to be able to Verify that the credential is not revoked at the given time (any time in the past).       
1. Querying
    1. One needs to be able to get all CRED_DEFs created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs with the given name created by the given Issuer DID.
    1. One needs to be able to get all SCHEMAs with the given name and version created by the given Issuer DID.
    1. One needs to be able to get all REVOC_REGs created by the given Issuer DID.
    1. One needs to be able to get all REVOC_REGs created by the given Issuer DID for the given CRED_DEF.    

## Referencing Anoncreds Entities

<b>Reqs 4</b>

The proposed solution is to identify entities by a unique `id`.
 * State-Trie-based key will be used as `id`. 
 This is the actual key used to store the entities in Patricia Merkle State Trie.
 * It can be deterministically calculated from the primary key tuples (by the client).
 * This single value will be used in anoncreds protocol (in libindy) to identify entities.
 * This ID should be included in all transactions as a new field (`id`).
 * We may expect changes in the format of this field, so it's not just address (key)
 in the State Trie, but can be a descriptive identifier.
 * The `id` attribute is calculated by the client and send as a part of SCHEMA/CRED_DEF/REVOC_REG_DEF txns.
 The ledger doesn't use this key as it is for storing the data in the State Trie.
 The ledger also calculates the key on its side from the primary key tuples, compares it with the provided `id`,
 and orders it only if they match. The request is rejected if they don't match.
 * We need to support [`GET_OBJ`](.get_obj) request to get the current state of the Schema/CredDef/RevocReg by its `id`.

      
## SCHEMA 

<b>Reqs 1, 4, 8</b>

#### SCHEMA txn
```
{
    "data": {
        "id":"L5AD5g65TDQr1PPHHRoiGf1Degree1.0",
        "attrNames": ["undergrad","last_name","first_name","birth_date","postgrad","expiry_date"],
        "name":"Degree",
        "version":"1.0",
    },
    
    "reqMetadata": {
        "submitterDid":"L5AD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```

#### Restrictions

* Existing Schema (identified by the Schema `id`) can not be modified/changed/evolved.
A new Schema with a new name/version needs to be issued if one needs to evolve it.
* Only the `submitterDid` who created the Schema can modify it (that is we need to keep the ownership).
* `id` field must match the State Trie key (address) for this Schema.

#### State

* key: `schemasubmitterDid | SchemaMarker | schemaName | schemaVersion` 
* value: aggregated txn `data` and `txnMetadata` (as in ledger)


#### GET_SCHEMA
Gets a Schema by ID.
```
{
    "data": {
        "id":"L5AD5g65TDQr1PPHHRoiGf1Degree1.0",
    },
...
}
```

#### LIST_SCHEMA
Gets the list of schemas according to the given filters.
```
{
    "data": {
        "submitterDid":"L5AD5g65TDQr1PPHHRoiGf",
        "name":"Degree", (optional)
        "version":"1.0", (optional)
    },
...
}
```
The filters can be applied in the following order: `submitterDid` -> `name` -> `version`.

## CRED_DEF

<b>Reqs 2, 4, 5, 8</b>

The Definition of credentials for the given Schema by the given Issuer.
It contains public keys (primary and revocation),
signature type and reference to the Schema. 

#### CRED_DEF txn
```
{
    "data": {
        "id":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1",
        "type":"CL",
        "tag": "key1",
        "schemaId":"L5AD5g65TDQr1PPHHRoiGf1Degree1",
        "value": {
            "publicKeys": {},            
        }
    },
    
    "reqMetadata": {
        "submitterDid":"HHAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
 

#### Restrictions

* Existing CredDef (identified by the CredDef `id`) can be modified/changed/evolved.
That is rotation of keys is supported.
* Only the `submitterDid` created the CredDef can modify it (that is we need to keep the ownership). 
* `id` field must match the State Trie key (address) for this CredDef.

#### State

* key: `credDefsubmitterDid | CredDefMarker | schemaID | signatureType | credDefTag` 
* value: aggregated txn `data` and `txnMetadata` (as in ledger)


#### GET_CRED_DEF
Gets a CredDef by ID.
```
{
    "data": {
        "id":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1",
    },
...
}
```

#### LIST_CRED_DEF
Gets a list of CredDefs according to the given filters.
```
{
    "data": {
        "submitterDid":"L5AD5g65TDQr1PPHHRoiGf",
        "schemaId":"L5AD5g65TDQr1PPHHRoiGf1Degree1",    (optional)
        "type":"CL",    (optional)
        "tag": "key1",    (optional)
    },
...
}
```
The filters can be applied in the following order: `submitterDid` -> `schemaId` -> `type` -> `tag`.

### REVOC_REG_DEF

<b>Reqs 3, 4, 8</b>

The Definition of revocation registry for the given CredDef.
It contains public keys, maximum number of credentials the registry may contain,
reference to the CredDef, plus some revocation registry specific data.

#### REVOC_REG_DEF txn
```
{
    "data": {
        "id":"MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "revocDefType":"CL_ACCUM",
        "tag": "reg1",
        "credDefId":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1",
        "value": {
            "issuanceType": "<issued by default or not>",
            "maxCredNum": 1000000,
            "publicKeys": {},
            "tailsHash": "<SHA256 hash>",
            "tailsLocation": "<URL>"
        }
    },
    
    "reqMetadata": {
        "submitterDid":"MMAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
* `id` (string, ":" as a field separator): ID as a key in State Trie.
* `revocDefType` (enum string): Revocation Registry type (only `CL_ACCUM` is supported for now).

    Revocation Registry is updated only during each issuance and  revocation.
* `credDefId` (string): ID of the corresponding CredDef
* `tag` (string): unique descriptive ID of the Registry.
* `value` (json): Registry-specific data.
    * `issuanceType` (enum string): Type of Issuance:
        * `ISSUANCE_BY_DEFAULT`: all indices are assumed to be issued and initial accumulator is calculated over all indices; 
        Revocation Registry is updated only during revocation.
        * `ISSUANCE_ON_DEMAND`: nothing is issued initially accumulator is 1; 
    * `maxCredNum` (int): maximum number of credentials the Registry can serve.
    * `publicKeys` (json): Registry's public key.        
    * `tailsHash` (string): hash of tails.
    * `tailsLocaiton` (string): location of tails file. 
 

#### Restrictions

* Existing RevocRegDef (identified by the RevocRegDef `id`) can be modified/changed/evolved.
That is rotation of keys is supported.
* Only the `submitterDid` who created the RevocRegDef can modify it (that is we need to keep the ownership). 
* `id` field must match the State Trie key (address) for this RevocRegDef.

#### State

* key: `revocDefSubmitterDid | RevocRegMarker | credDefID | revocDefType | revocDefTag` 
* value: aggregated txn `data` and `txnMetadata` (as in ledger)
* RevocRegMarker = "\04"



#### GET_REVOC_REG_DEF
Gets a RevocRegDef by ID.
```
{
    "data": {
        "id":"MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
    },
...
}
```

#### LIST_REVOC_REG_DEF
Gets a list of RevocRegDefs according to the given filters.
```
{
    "data": {
        "submitterDid":"MMAD5g65TDQr1PPHHRoiGf",
        "credDefId":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1",   (optional)
        "revocDefType":"CL_ACCUM",   (optional)
        "tag": "reg1",    (optional)
    },
...
}
```
The filters can be applied in the following order: `submitterDid` -> `credDefId` -> `type` -> `tag`.

### REVOC_REG_ENTRY

<b>Reqs 3, 4, 8</b>

The RevocReg entry containing the new accumulator value and issued/revoked indices. This is juat a delta of indices, not 
the whole list.
So, it can be sent each time a new claim is issued/revoked.

#### REVOC_REG_ENTRY txn
```
{
    "data": {
        "revocRegDefId": "MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "revocDefType":"CL_ACCUM",
        "value": {
            "prevAccum":"<prev_accum_value>", (optional)
            "accum":"<accum_value>",
            "issued": [], (optional)
            "revoked": [], (optional)
        }
    },
    
    "reqMetadata": {
        "submitterDid":"MMAD5g65TDQr1PPHHRoiGf",
        .....
    },
    
....
}
```
* `revocRegId` must match an existing `REVOC_REG_DEF` with the given `id`.
* `entry`: Registry-specific entry:
    * `issued`: an array of issued indices (may be absent/empty if the type is "issuance by default"); this is delta; will be accumulated in state.
    * `revoked`: an array of revoked indices (delta; will be accumulated in state)
    * `prevAccum`: previous accumulator value; it's compared with the current value, and txn is rejected if they don't match;
    it's needed to avoid dirty writes and updates of accumulator. 
    * `accum`: current accumulator value

#### Restrictions

* Existing RevocRegEntry (identified by the RevocRegDef's `id`) can be modified/changed/evolved.
* Only the `submitterDid` who created the corresponding `REVOC_REG_DEF` can modify it. 
* Submitter must specify the previous value of accumulator. It's compared with the current value, and txn is rejected if they don't match.
This is needed to avoid dirty writes and updates of accumulator. 


#### State

* key: `revocDefSubmitterDid | RevocRegEntryMarker | revocRegDefId`

* value: aggregated txn `data` and `txnMetadata` (as in ledger); 
contains aggregated accum_value, issued and revoked arrays.

* RevocRegEntryMarker = "\05"

<b>Hint</b>: We should consider using BitMask to store the current aggregated state of issued and revoked arrays
in the State Trie to reduce the required space.

<b>Additional</b>: For `GET_REVOC_REG` and `GET_REVOC_REG_DELTA` transactions we should save `ACCUM` value 
into different state record (state proof purposes):

* key: `revocDefSubmitterDid | RevocRegEntryAccumMarker | revocRegDefId`

* value: aggregated txn `data` and `txnMetadata` (as in ledger) with only accum value without issued and revoked arrays.

    * Schema of "pruned" `data` from txn must be:
        ```
        {
            "data": {
                "revocRegDefId": "MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
                "revocDefType":"CL_ACCUM",
                "value": {
                    "accum":"<accum_value>",
                }
            },    
        ....
        }
        ```
        
* RevocRegEntryAccumMarker = "\06"
    

#### GET_REVOC_REG
Gets the accumulated state of the Revocation Registry by ID
The state is defined by the given  `timestamp`.
Returns just the current accumulator value for `CL_ACCUM` type.

Request: 
```
{
    "data": {
        "revocRegDefId":"MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "timestamp": 20,
    },
...
}
```
Reply:
```
{
    "data": {
        "revocRegDefId": "MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "revocDefType":"CL_ACCUM",
        "value": {
            "accum":"<accum_value>",
        }
    },
....
}
```

See next sections on how to get the state for the given `timestamp`. 

#### GET_REVOC_REG_DELTA
Gets the Delta of the accumulated state of the Revocation Registry.
The Delta is defined by `from` and `to` timestamp fields.
If `from` is not specified, then the whole state till `to` will be returned.

For `CL_ACCUM` type it returns the accumulator value at time `to` plus a Delta of issued and revoked indices.

Request: 
```
{
    "data": {
        "revocRegDefId": "MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "from": 20, (optional)
        "to": 40
    },
...
}
```
Reply:
```
{
    "data": {
        "revocRegId": "MMAD5g65TDQr1PPHHRoiGf:3:HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1Degree1CLkey1:CL_ACCUM:reg1",
        "revocDefType":"CL_ACCUM",
        "stateProofFrom": <state proof for accum by timestamp 'from'>  (if "from" parameter is presented in request)
        "value": {
            "accum_to": "<accum_value from ledger for timestamp 'to'>",
            "accum_from": "<accum_value from ledger for timestamp 'from'>" (if "from" parameter is presented in request)
            "issued": [1, 45], 
            "revoked": [56, 78, 890],
        }
    },
....
}
```
Notes:
* accum_to and accum_from it's a transactions from ledger "as-is", 
like reply for for GET_REVOC_REG query.
* general STATE_PROOF in reply is:
  * STATE_PROOF for "to" accum value if "from" was found.
  * STATE_PROOF for REG_ENTRY transaction if "from" was not found or not presented in request

See next sections on how to get the state for the given timestamp. 

## Timestamp Support in State

<b>Reqs 6, 7</b>

We need to have a generic way to get the State at the given time.
- State Trie allows to go to the past, that is given the root hash, get the state with this root.
- We may have a mapping of each State update (timestamp) to the corresponding root.
- We need to find a data structure that can help us to find the nearest state timestamp (to get the root) for the given
time.
- So, we will be able to get the data (state) at the given time.

This approach can be used for
* getting `REVOC_REG_ENTRY` at desired time (the same for both proper and verifier),
possibly long ago in the past;
* dealing with Requirement 6. 

<b>Example</b>:
* There are the following entries (in key-value storage): 
    * `ts1` - `root1`
    * `ts2` - `root2`
* We need to find the nearest root for ts3, where `ts1 < ts3 < ts2`.
    * So, we need to return `root1`


## Issuer Key Rotation

<b>Reqs 6</b>

#### Changes in Anoncreds Protocol

If want to support Requirement 6, then the following changes are required in the
anoncerds protocol:

* Each Credential must have a reserved mandatory attribute: `issuanceTime`.
    * It's set by the Issuer to specify the time of Issuance.
    * It's needed to fulfill Requirements 5.
* This attribute can be considered as `m3` special attribute (`m1` is master secret, `m2` is credential context, `m3` is issuance time).
* Since the Issuer may be malicious (if keys were compromised already), then 
a proof that `issuanceTime` is really the current time and not the time from the past is needed.
    * We can use our blockchain to prepare such a proof.
    * Issuer signs (by his Cred Def's public key) the `issuanceTime` and sends it to the pool.
    * Each node verifies that `issuanceTime` is not less that the current one, and signs the result with BLS key.
    * Each node then sends the signed result to the Issuer (no need to write anything to the ledger).
    * The issuer prepares a BLS multi-signature (making sure that there is a consensus)
    and adds the BLS-signed proof of the `issuanceTime` to the credential.
    * The verifier will then use the proof to make sure that the `issuanceTime` is really the correct one.
* The `issuanceTime` needs to be verified in each proof.
    * The Verifier should use Predicates (instead of disclosing) for the value of `issuanceTime`
    to avoid correlation. 
    * It's possible also to disclose `issuanceTime`, but we don't force it.
    * If it's not disclosed and not verified as a Predicate, then there is a chance the the proof verification will fail because 
of key rotations, since the latest keys will be used.

#### Changes in Transactions
A new field `oldKeyTrustTime` needs to be added to `CRED_DEF` and `REVOC_REF_DEF` txns.
`oldKeyTrustTime` can be set each time a key is rotated and defines
 `the intervals when we still can trust the previous value of the key`. 
It is needed to deprecate credentials issued during the time when we suspect
the keys were stolen.
We can not always use revocation to deprecate old credentials, since revocation keys can
be stolen as well.  


#### How oldKeyTrustTime works
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
1. At `timeA`:
 ```
 "data": {
        "uuid":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key1},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
    },
```
2. At `timeC`:   
 ```
 "data": {
        "uuid":"TYzcdDLhCpGCYRHW82kjHd",
        "publicKeys": {key2},
        "schemaRef":"GEzcdDLhCpGCYRHW82kjHd",
        "signatureType":"CL",
        "oldKeyTrustTime": {          
            ("from": "A", "to": "B"),
            ("from": "C"),
        }
    },
```
3. At `timeE`:   
 ```
 "data": {
        "uuid":"TYzcdDLhCpGCYRHW82kjHd",
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
        "uuid":"TYzcdDLhCpGCYRHW82kjHd",
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

#### Changes in GET request

An optional field `issuanceTime` needs to be supported for 
* `GET_CRED_DEF`
* `GET_REVOC_REG_DEF`
* `GET_OBJ`.

There is a special logic to get the valid and trusted value of the keys
depending on the issuance time:
1. Lookup State Trie to get the current state by the key (either `id` in case of `GET_OBJ` or a key created
from primary key fields provided in the request).
1. If no `issuanceTime` provided, then just return the current value.  
1. Try to find the interval (in `oldKeyTrustTime` array) the `issuanceTime` belongs to.
    * If it's greater than the most right interval, then return the current value.
    * If it belongs to an interval, then get the left value (`from`) of the interval.
    * If it's in between intervals, then get the right interval, and get the left value (`from`)
of this interval.
1. Use generic logic to get the root of the State trie at the time `to` found above. 
1. Lookup State Trie with the found root to find the state at that time (the same way as in Step 1)

So, we will have not more than 2 lookups for each request. 

Result for the Example above:
* `issuanceTime < A` => [A,B] => state at timeA => key1 (OK)
* `A <= issuanceTime <= B` => [A,B] => state at timeA => key1 (OK)
* `B < issuanceTime < C` => [C,D] => state at timeC => key2 (deprecated credentials)
* `C <= issuanceTime <= D` => [C,D] => state at timeC => key2 (OK)
* `D < issuanceTime < E` => [E,...] => state at timeE => key3 (deprecated credentials)
* `issuanceTime > E` => [E,...] => state at timeE => key3 (OK)