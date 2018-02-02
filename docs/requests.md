# Requests
* [Common Request Structure](#common-request-structure)
* [Common Reply Structure](#common-reply-structure)
* [ACK Structure](#ack-structure)
* [NACK Structure](#nack-structure)
* [Reject Structure](#reject-structure)
* [Write Requests](#write-requests)

    * [NYM](#nym)    
    * [ATTRIB](#attrib)    
    * [SCHEMA](#schema)
    * [CLAIM_DEF](#claim_def)
    * [NODE](#node)
    * [POOL_UPGRADE](#pool_upgrade)
    * [POOL_CONFIG](#pool_config)

* [Read Requests](#read-requests)

    * [GET_NYM](#get_nym)    
    * [GET_ATTRIB](#get_attrib)    
    * [GET_SCHEMA](#get_schema)
    * [GET_CLAIM_DEF](#get_claim_def)
    * [GET_TXN](#get_txn)
    
This doc is about supported client"s Request (both write and read ones).
If you are interested in transactions and their representation on the Ledger (that is internal one),
then have a look at [transactions](transactions.md).

[indy-sdk](https://github.com/hyperledger/indy-sdk) expects the format as specified below.

See [roles and permissions](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0) on the roles and who can create each type of transactions.

## Common Request Structure

Each Request (both write and read) is a JSON with a number of common metadata fields.

```
{
    "reqType": <...>,
    "reqVersion": <...>,
    "protocolVersion": <...>,
    
    "data": {
        <request-specific fields>
    },
    "reqMetadata": {
        "reqId": <...>,
        "submitterDID": <...>,
    },
    "reqSignature": {
        "type": <...>,
        "value": <...>
    }   
}
```

- `reqType` (enum integer):
 
    Request type as one of the following values:

    - NODE = 0
    - NYM = 1
    - ATTRIB = 100
    - SCHEMA = 101
    - CLAIM_DEF = 102
    - POOL_UPGRADE = 109
    - NODE_UPGRADE = 110
    - POOL_CONFIG = 111
    - GET_TXN = 3
    - GET_ATTR = 104
    - GET_NYM = 105
    - GET_SCHEMA = 107
    - GET_CLAIM_DEF = 108
        
- `reqVersion` (integer):

    Request version to be able to evolve requests.
    The content of "data" and "reqMetadata" fields may depend on the version.  

- `protocolVersion` (integer; optional): 

    The version of client-to-node protocol. Each new version may introduce a new feature in Requests/Replies/Data.
    Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
    between clients and nodes.     

- `data` (json):

    Request-specific data.

- `reqMetadata` (json):

    Metadata coming with the Request and saving in the transaction as is (if this is a write request).

    - `submitterDID` (base58-encoded string):
         Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
         for 16 or 32 bit DID value.
         It must be present on Ledger for write requests and can be any value for read requests.
         
         It may differ from `did` field for some of requests (for example NYM), where `did` is a 
         target identifier (for example, a newly created DID identifier).
         
         *Example*: `submitterDID` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
         
    - `reqId` (integer): 
        Unique ID number of the request with transaction.
        
- `reqSignature` (json):

    Submitter's signature over "data" and "reqMetadata".
    
    - `type` (enum number as integer):
        
        - ED25519: ed25519 signature
        - ED25519_MULTI: ed25519 signature in multisig case.
    
    - `value` (base58-encoded string or array of base58-encoded string): signature value    

Please find the format of each request-specific data for each type of request below.

## Common Reply Structure 

Each Reply to requests has a number of common metadata fields and state-proof related fields.
Please note that state-proof is absent for write requests Reply since  
(we don"t support State Proofs for write requests yet). Most of these fields are actually metadata fields 
of a transaction in the Ledger (see [transactions](transactions.md)).

```
{
    "op": "REPLY",
    
    "reqType": <...>,
    "reqVersion": <...>,
    "protocolVersion": <...>,
    
    "reqMetadata": {
        "reqId": <...>,
        "submitterDID": <...>,
    },
    "reqSignature": {
        "type": <...>,
        "value": <...>
    },
    
    "txn": {
        <txn as in ledger>
    },
     
    "ledgerMetadata": {
        "ledgerId": <...>, 
        "rootHash": <...>,
        "size": <...>,
    },

    "stateMetadata": {
        "timestamp": <...>,
        "poolRootHash": <...>,
        "rootHash": <...>,
    },

    "poolMultiSignature": {
        "type": <...>,
        "value": <...>,
        "participants": <...>
    }, 

    "stateProof": <...>,
    "auditProof": <...>, 

}

```

- `reqType` (enum number as string): 

    Request types (as in Request).
    
- `reqVersion` (string):

    Request version (as in Request).

- `protocolVersion` (integer; optional): 

    The version of client-to-node protocol (as in Request).
    
- `reqMetadata` (json; optional):

    Metadata as in Request. It may be absent for Reply to write requests as `txn` fields already contains 
    this information as part of transaction written to the ledger.
    
- `txn` (json): 

    Transaction as written to the Ledger (see [transactions](transactions.md)).
    Includes transaction data, request metadata (as was in Request) and transaction metadata.

- `ledgerMetadata` (json):

    Metadata associated with the current state of the Ledger.

    - `ledgerId` (enum integer):
        ID of the ledger the transaction is written to:
        - POOL_LEDGER = 0
        - DOMAIN_LEDGER = 1
        - CONFIG_LEDGER = 2
    
    - `rootHash` (base58-encoded hash string):
        base58-encoded ledger"s merkle tree root hash
        
    - `size` (integer):
        Ledger"s size (that is the last seqNo present at the ledger at that time).
        
- `stateMetadata` (json):

    Metadata associated with the state (Patricia Merkle Trie) the returned transaction belongs to
    (see `ledgerId`).
    
    - `timestamp` (integer as POSIX timestamp):
     last update of the state
         
    - `poolRootHash` (base58-encoded hash string):
     pool state trie root hash to get the current state of the Pool
     (it can be used to get the state of the Pool at the moment the BLS multi-signature was created).
        
    - `rootHash` (base58-encoded string):
     state trie root hash for the ledger the returned transaction belongs to

- `poolMultiSignature` (json):
 
    Nodes' Multi-signature against the given `ledgerMetadata` and `stateMetadata` (serialized to MsgPack)
    - `value` (enum string): multi-signature type
        - BLS: BLS multi-signature
    - `value` (base58-encoded string): the value of the BLS multi-signature
    - `participants` (array os strings): Aliases of Nodes participated in BLS multi-signature (the number of participated nodes is not less than n-f)

- `stateProof` (base64-encoded string; optional): 

    Patricia Merkle Trie State proof for the returned transaction.
    It proves that the returned transaction belongs to the Patricia Merkle Trie with a
    root hash as specified in `stateMetadata`.
    It is present for replies to read requests only (except GET_TXN Reply).
    
- `auditProof` (array of base58-encoded hash strings; optional):

    Ledger's merkle tree audit proof as array of base58-encoded hash strings.
    This is a cryptographic proof to verify that the returned transaction has 
    been appended to the ledger with the root hash as specified in `ledgerMetadata`.
    It is present for replies to write requests only, and GET_TXN Reply.
    
## ACK Structure
```
{
    "op": "REQACK",
    
    "reqType": <...>,
    "reqVersion": <...>,
    "protocolVersion": <...>,
    
    "reqMetadata": {
        "reqId": <...>,
        "submitterDID": <...>,
    }
}

```


## NACK Structure
```
{
    "op": "REQNACK",
    
    "reqType": <...>,
    "reqVersion": <...>,
    "protocolVersion": <...>,
    
    "reqMetadata": {
        "reqId": <...>,
        "submitterDID": <...>,
    },
    
    "reason": <reason_str>
}

```
## Reject Structure
```
{
    "op": "REQNACK",
    
    "reqType": <...>,
    "reqVersion": <...>,
    "protocolVersion": <...>,
    
    "reqMetadata": {
        "reqId": <...>,
        "submitterDID": <...>,
    },
    
    "reason": <reason_str>
}

```
 

## Write Requests

The format of each request-specific data for each type of request.

### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and trustee can be created only by other trusties (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).

The request can be used for 
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.

- `did` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterDID` metadata field, where `submitterDID` is the DID of the submitter.
    
    *Example*: `submitterDID` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
     
- `role` (enum number as integer; optional): 

    Role of a user NYM record being created for. One of the following numbers
    
    - None (common USER)
    - 0 (TRUSTEE)
    - 2 (STEWARD)
    - 101 (TRUST_ANCHOR)
    
  A TRUSTEE can change any Nym's role to None, this stopping it from making any writes (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).
  
- `verkey` (base58-encoded string; optional): 

    Target verification key as base58-encoded string. If not set, then either the target identifier
    (`did`) is 32-bit cryptonym CID (this is deprecated), or this is a user under guardianship
    (doesnt owns the identifier yet).

- `alias` (string; optional): 

    NYM's alias.
    

If there is no NYM transaction with the specified DID (`did`), then it can be considered as creation of a new DID.

If there is a NYM transaction with the specified DID (`did`),  then this is update of existing DID.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if key rotation needs to be performed, the owner of the DID needs to send a NYM request with
`did` and `verkey` only. `role` and `alias` will stay the same.


*Request Example*:
```
{

    "reqType": 1,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "did": "N22KY2Dyvmuu2PyyqSFKue",
        "role": "101",
        "verkey": "31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE"
    },
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 1,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    
    "txn": {
        "txnType": 1,
        "txnVersion": 1,
        "data": {
            "did": "N22KY2Dyvmuu2PyyqSFKue",
            "role": "101",
            "verkey": "31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE"
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 300,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    },

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```

### ATTRIB

Adds attribute to a NYM record.

- `did` (base58-encoded string):

    Target DID we set an attribute for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterDID` metadata field, where `submitterDID` is the DID of the submitter.
    
    *Example*: `submitterDID` is a DID of a Trust Anchor setting an attribute for a DID, and `did` is the DID we set an attribute for.
    
- `raw` (json; mutually exclusive with `hash` and `enc`):

    Raw data is represented as json, where key is attribute name and value is attribute value.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute data.

*Request Example*:
```
{

    "reqType": 100,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "did": "N22KY2Dyvmuu2PyyqSFKue",
        "raw": "{"name": "Alice"}"
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },    
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 100,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    
    "txn": {
        "txnType": 100,
        "txnVersion": 1,
        "data": {
            "did": "N22KY2Dyvmuu2PyyqSFKue",
            "raw": "{"name": "Alice"}"
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 301,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 301,
    }

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```


### SCHEMA
Adds Claim's schema.

It's not possible to update existing Schema.
So, if the Schema needs to be evolved, a new Schema with a new version or name needs to be created.

- `uuid` (base58-encoded string):

    Schema's UUID as base58-encoded string for 16 or 32 bit DID value. It must be unique within the ledger.
    It differs from `submitterDid` metadata field, where `submitterDid` is the DID of the submitter.
    
    *Example*: `submitterDid` is a DID of a Schema Author, and `uuid` is Schema's unique UUID.

- `attrNames` (array of strings):
 
    Array of attribute name strings.

- `name` (string):
 
    Schema's name string.

- `version` (string):
 
    Schema's version string

*Request Example*:
```
{

    "reqType": 101,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "uuid":"sdfghj65TDQr1PPHHRoiGf",
        "version": "1.0",
        "name": "Degree",
        "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 101,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    
    "txn": {
        "txnType": 101,
        "txnVersion": 1,
        "data": {
            "uuid":"sdfghj65TDQr1PPHHRoiGf",
            "version": "1.0",
            "name": "Degree",
            "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
        }
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 302,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 302,
    },

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```


### CLAIM_DEF
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema.

It's not possible to update `data` in existing Claim Def.
So, if a Claim Def needs to be evolved (for example, a key needs to be rotated), then
a new Claim Def needs to be created by a new Issuer DID (`did`).

- `uuid` (base58-encoded string):

    Claim Def's UUID as base58-encoded string for 16 or 32 bit DID value. It must be unique within the ledger.
    It differs from `submitterDid` metadata field, where `submitterDid` is the DID of the submitter.
    
    *Example*: `submitterDid` is a DID of the ClaimDef Issuer, and `uuid` is the Claim Def's UUID.

- `publicKeys` (dict):
 
     Dictionary with Claim Definition's public keys:
     
    - `primary`: primary claim public key
    - `revocation`: revocation claim public key
        
- `schemaRef` (string):
    
    Sequence number of a Schema transaction the claim definition is created for.

- `signatureType` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.


*Request Example*:
```
{

    "reqType": 102,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "uuid":"cvbnmh65TDQr1PPHHRoiGf",
        "signatureType": "CL",
        "schemaRef":"sdfghj65TDQr1PPHHRoiGf",
        "publicKeys": {
            "primary": ....,
            "revocation": ....
        }
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
       "type": "ED25519",
       "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 102,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    
    "txn": {
        "txnType": 102,
        "txnVersion": 1,
        "data": {
            "uuid":"cvbnmh65TDQr1PPHHRoiGf",
            "signatureType": "CL",
            "schemaRef": "sdfghj65TDQr1PPHHRoiGf",    
            "publicKeys": {
                "primary": ....,
                "revocation": ....
            }
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 302,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 302,
    },

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```

### NODE
Adds a new node to the pool, or updates existing node in the pool.

- `did` (base58-encoded string):

    Target Node's DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterDID` metadata field, where `submitterDID` is the DID of the transaction submitter (Steward"s DID).
    
    *Example*: `submitterDID` is a DID of a Steward creating a new Node, and `did` is the DID of this Node.
    
- `verkey` (base58-encoded string; optional): 

    Target Node verification key as base58-encoded string.
    It may absent if `did` is 32-bit cryptonym CID. 

- `alias` (string): 
    
    Node's alias
    
- `blskey` (base58-encoded string; optional):
 
    BLS multi-signature key as base58-encoded string (it's needed for BLS signatures and state proofs support)
    
- `clientIp` (string; optional): 
    
    Node's client listener IP address, that is the IP clients use to connect to the node when sending read and write requests (ZMQ with TCP)
      
- `clientPort` (string; optional):

    Node's client listener port, that is the port clients use to connect to the node when sending read and write requests (ZMQ with TCP)
    
- `nodeIp` (string; optional):
 
    The IP address other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    
- `nodePort` (string; optional):
 
    The port other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    
- `services` (array of strings; optional):
 
    The service of the Node. `VALIDATOR` is the only supported one now.
     

If there is no NODE transaction with the specified Node ID (`did`), then it can be considered as creation of a new NODE.

If there is a NODE transaction with the specified Node ID (`did`), then this is update of existing NODE.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if a Steward wants to rotate BLS key, then it's sufficient to send a NODE transaction with `did` and a new `blskey`.
There is no need to specify all other fields, and they will remain the same.


*Request Example*:
```
{

    "reqType": 0,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "did": "6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8"
        "alias": "Node1",
        "clientIp": "127.0.0.1",
        "clientPort": 7588,
        "nodeIp": "127.0.0.1", 
        "nodePort": 7587,
        "blskey": "00000000000000000000000000000000",
        "services": ["VALIDATOR"]
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 0,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },    
    
    "txn": {
        "txnType": 0,
        "txnVersion": 1,
        "data": {
            "did": "6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8"
            "alias": "Node1",
            "clientIp": "127.0.0.1",
            "clientPort": 7588,
            "nodeIp": "127.0.0.1", 
            "nodePort": 7587,
            "blskey": "00000000000000000000000000000000",
            "services": ["VALIDATOR"]
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },        
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 10,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 0, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 10,
    },

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```

### POOL_UPGRADE

Command to upgrade the Pool (sent by Trustee). It upgrades the specified Nodes (either all nodes in the Pool, or some specific ones).

- `name` (string):

    Human-readable name for the upgrade.

- `action` (enum: `start` or `cancel`):

    Starts or cancels the Upgrade.
    
- `version` (string):

    The version of indy-node package we perform upgrade to.
    Must be greater than existing one (or equal if `reinstall` flag is True).
    
- `schedule` (dict of node DIDs to timestamps):

    Schedule of when to perform upgrade on each node. This is a map where Node DIDs are keys, and upgrade time is a value (see example below).
    If `force` flag is False, then it's required that time difference between each Upgrade must be not less than 5 minutes
    (to give each Node enough time and not make the whole Pool go down during Upgrade).
    
- `sha256` (sha256 hash string):

    sha256 hash of the package
    
- `force` (boolean; optional):

    Whether we should apply transaction (schedule Upgrade) without waiting for consensus
    of this transaction.
    If false, then transaction is applied only after it's written to the ledger.
    Otherwise it's applied regardless of result of consensus, and there are no restrictions on the Upgrade `schedule` for each Node.
    So, we can Upgrade the whole Pool at the same time when it's set to True.  
    False by default. Avoid setting to True without good reason.

- `reinstall` (boolean; optional):

    Whether it's allowed to re-install the same version.
    False by default.

- `timeout` (integer; optional):

    Limits upgrade time on each Node.

- `justification` (string; optional):

    Optional justification string for this particular Upgrade.

*Request Example*:
```
{

    "reqType": 109,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "name": `upgrade-13`,
        "action": `start`,
        "version": `1.3`,
        "schedule": {"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
        "sha256": `db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55`,
        "force": false,
        "reinstall": false,
        "timeout": 1
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 109,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },         
    
    "txn": {
        "txnType": 109,
        "txnVersion": 1,
        "data": {
            "name": `upgrade-13`,
            "action": `start`,
            "version": `1.3`,
            "schedule": {"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
            "sha256": `db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55`,
            "force": false,
            "reinstall": false,
            "timeout": 1
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },        
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 45,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 2, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 45,
    },

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```

### POOL_CONFIG


Command to change Pool's configuration

- `writes` (boolean):

    Whether any write requests can be processed by the pool (if false, then pool goes to read-only state).
    True by default.


- `force` (boolean; optional):

    Whether we should apply transaction (for example, move pool to read-only state) without waiting for consensus
    of this transaction.
    If false, then transaction is applied only after it's written to the ledger.
    Otherwise it's applied regardless of result of consensus.  
    False by default. Avoid setting to True without good reason.

*Request Example*:
```
{

    "reqType": 111,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "writes":false,
        "force":true
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 111,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    "reqSignature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },       
    
    "txn": {
        "txnType": 111,
        "txnVersion": 1,
        "data": {
            "writes":false,
            "force":true
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },           
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 46,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 2, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 46,
    }

    "stateMetadata": {
        "timestamp": 1514214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```

## Read Requests

### GET_NYM
Gets information about a DID (NYM).

- `did` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterDID` metadata field, where `submitterDID` is the DID of the sender (may not exist on ledger at all).

*Request Example*:
```
{

    "reqType": 105,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "did": "2VkbBskPNNyWrLrZq7DBhk"
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 105,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    
    "txn": {
        "txnType": 1,
        "txnVersion": 1,
        "data": {
            "did": "2VkbBskPNNyWrLrZq7DBhk",
            "role": "101",
            "verkey": "31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE"
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },           
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 46,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    }

    "stateMetadata": {
        "timestamp": 1524214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=", 
}
```


### GET_ATTRIB
Gets information about an Attribute for the specified DID.

- `did` (base58-encoded string):

    Target DID we get an attribute for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterDID` metadata field, where `submitterDID` is the DID of the sender (may not exist on ledger at all).
    
- `raw` (string; mutually exclusive with `hash` and `enc`):

    Requested attribute name.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Requested attribute hash.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute. 

*Request Example*:
```
{

    "reqType": 104,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "did": "AH4RRiPR78DUrCWatnCW2w",
        "raw": "dateOfBirth"
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 104,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    
    "txn": {
        "txnType": 100,
        "txnVersion": 1,
        "data": {
            "did": "AH4RRiPR78DUrCWatnCW2w",
            "raw": "{"name": "Alice"}"
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },           
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 301,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    }

    "stateMetadata": {
        "timestamp": 1524214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=", 
}
```

### GET_SCHEMA

Gets Claim's Schema.

- `uuid` (base58-encoded string):

    Schema's UUID as base58-encoded string for 16 or 32 bit DID value. It must be unique within the ledger.
    It differs from `submitterDid` metadata field, where `submitterDid` is the DID of the submitter.
    
    *Example*: `submitterDid` is a DID of a Schema Author, and `uuid` is Schema's unique UUID.

    
*Request Example*:
```
{

    "reqType": 107,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "uuid":"sdfghj65TDQr1PPHHRoiGf",
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 107,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    
    "txn": {
       "txnType": 101,
        "txnVersion": 1,
        "data": {
            "uuid":"sdfghj65TDQr1PPHHRoiGf",
            "version": "1.0",
            "name": "Degree",
            "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },        
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 302,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    }

    "stateMetadata": {
        "timestamp": 1524214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=", 
}
```
 
### GET_CLAIM_DEF

Gets Claim Definition.

- `uuid` (base58-encoded string):

    Claim Def's UUID as base58-encoded string for 16 or 32 bit DID value. It must be unique within the ledger.
    It differs from `submitterDid` metadata field, where `submitterDid` is the DID of the submitter.
    
    *Example*: `submitterDid` is a DID of the ClaimDef Issuer, and `uuid` is the Claim Def's UUID.

*Request Example*:
```
{

    "reqType": 108,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "uuid":"cvbnmh65TDQr1PPHHRoiGf",
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    
    "reqType": 108,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    },
    
    "txn": {
        "txnType": 102,
        "txnVersion": 1,
        "data": {
            "uuid":"cvbnmh65TDQr1PPHHRoiGf",
            "signatureType": "CL",
            "schemaRef":"sdfghj65TDQr1PPHHRoiGf",
            "publicKeys": {
                "primary": ....,
                "revocation": ....
            }
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },           
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 302,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    },

    "stateMetadata": {
        "timestamp": 1524214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=", 
}
```

### GET_TXN

A generic request to get a transaction from Ledger by its sequence number.

- `ledgerId` (int enum):

    ID of the ledger the requested transaction belongs to (Pool=0; Domain=1; Config=2).

- `seqNo` (int):

    Requested transaction sequence number as it's stored on Ledger.

*Request Example (requests a NYM txn with seqNo=9)*:
```
{

    "reqType": 3,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "data": {
        "ledgerId": "1",
        "seqNo": 9,
    },
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
}
```

*Reply Example (returns a NYM txn with seqNo=9)*:
```
{
    "op": "REPLY",
    
    "reqType": 3,
    "reqVersion": 1,
    "protocolVersion": 1,
    
    "reqMetadata": {
        "reqId": 1514215425836443,
        "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
    }
    
    "txn": {
        "txnType": 1,
        "txnVersion": 1,
        "data": {
            "did": "2VkbBskPNNyWrLrZq7DBhk",
            "role": "101",
            "verkey": "31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE"
        },
        "reqMetadata": {
            "reqId": 1514215425836443,
            "submitterDID": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
            "type": "ED25519",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },           
        "txnMetadata": {
            "creationTime": 1514211268,
            "seqNo": 9,
        }
    },
     
    "ledgerMetadata": {
        "ledgerId": 1, 
        "rootHash": "DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr",
        "size": 300,
    }

    "stateMetadata": {
        "timestamp": 1524214795,
        "poolRootHash": "TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj",
        "rootHash": "7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK",
    },

    "poolMultiSignature": {
        "type": "BLS",
        "value": "RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b",
        "participants": ["Delta", "Gamma", "Alpha"]
    }, 

    "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"], 
}
```
