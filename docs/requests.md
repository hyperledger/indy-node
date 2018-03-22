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


## Base Client-to-Node and Node-to-Node serialization 

The main Client-to-Node and Node-to-Node envelope is serialized in MsgPack format.

## Common Message Structure

This is a common structure for ALL messages (both Node-to-Node and Client-to-Node).

```
{
    "type": <...>,
    "version": <...>,
    
    "from": <...>,
    "signature": {
        "type": <...>,
        "values": [
            "from": <...>,
            "value": <...>,
        ],
        "threshold": <...>
    },
    
    "serialization": <...>,
    "msg": <serialized-msg>
}
```
where the `msg` field has the following structure:
```
    "protocolVersion": <...>,
    "data": {
        "version": <...>,
        <msg-specific fields>
    },
    "metadata": {
        "version": <...>,
        <msg-specific fields>
    },
    "pluginData": {
        <plugin-specific-fields>
    }
```
- `type` (enum integer): 
 
    Msg type.
    
    
- `from` (base58-encoded string):
     Identifier (DID) of the message sender (a client or node who sent the transaction) as base58-encoded string
     for 16 or 32 bit DID value.
     It must be present on Ledger for write requests and can be any value for read requests.
     
     It may differ from `did` field for some of requests (for example NYM), where `did` is a 
     target identifier (for example, a newly created DID identifier).
     
     *Example*: `from` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.

- `signature` (dict, optional):

    Submitter's signature over serialized `msg` field.
    
    - `type` (string enum):
        
        - ED25519: ed25519 signature
        - ED25519_MULTI: ed25519 signature in multisig case.
    
    - `value` (base58-encoded string or array of base58-encoded string): signature value   
    
- `serialization` (string enum):

    Defines how the `msg` is serialized
     - JSON: json
     - MSG_PACK: msgpack
        
- `msg` (dict):
    
    Serialized message.

    - `protocolVersion` (integer; optional): 
    
        The version of client-to-node or node-to-node protocol. Each new version may introduce a new feature in Requests/Replies/Data.
        Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
        between clients and nodes.     
    
    - `data` (dict):
    
        Message-specific data.
    
    - `metadata` (dict):
    
        Message-specific metadata.

    - `pluginData` (dict):
    
        Plugin-specific data.

## Common Request Structure

Each Request (both write and read) follows the pattern as shown above.

```
{
    "from": <...>,
    "signature": {
        "type": <...>,
        "value": <...>
    },
    "serialization": <...>,
    "msg": {
        "type": <...>,
        "protocolVersion": <...>,
        "data": {
            "version": <...>,
            <msg-specific fields>
        },
        "metadata": {
            "version": <...>,
            "reqId": <...>,
            "from": <...>,
        },
    }
}
```

- `signature` is required for write requests only.

- Message Type `type` is one of the following values:

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

- `metadata` (dict):

    Metadata coming with the Request and saving in the transaction as is (if this is a write request).

    - `from` (base58-encoded string):
         Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
         for 16 or 32 bit DID value.
         It must be present on Ledger for write requests and can be any value for read requests.
         
         It may differ from `did` field for some of requests (for example NYM), where `did` is a 
         target identifier (for example, a newly created DID identifier).
         
         *Example*: `from` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
         
    - `reqId` (integer): 
        Unique ID number of the request with transaction.
        
- Please find the format of each request-specific data for each type of request below.

## Write/Read Reply Structure

Each Write/Read Reply follows the pattern as shown above.

```
{
    "from": <...>,
    "serialization": <...>,
    "msg": {
        "type": REPLY_WRITE/REPLY_READ,
        "protocolVersion": <...>,
        
        "data": {
            "version": <...>,
            "type": <...>,
            
            "results": [
                "result": {
                    <result>
                },
                "txnMetadata": {
                    <txn metadata as in ledger>
                },
                "reqSignature": {
                    <txn request signature as in ledger>
                }
                
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
            ]
        },
        "metadata": {
            "version": <...>,
            "reqId": <...>,
            "from": <...>,
        },
    }
}
```
- `type` (string):
    
    Request type as was in the corresponding Request. 
    
- `results` (array):

    Array of results. Each result may have either a state proof (it means that `result` is taken from state),
    audit proof (it means that `result` is taken from ledger), or no proofs (it means that this is some calculated data, and it's
    up to the client to verify it).

- `result` (dict): 

    The main result. It can be a transaction from state (see `state proof` then),
     a transaction from ledger (see `audit proof`), or any custom result.
    It usually includes transaction data and request metadata (as was in Request).

- `txnMetadata` (dict):

    Transaction metadata as stored in the Ledger.

- `reqSignature` (dict):

    Transaction's Request signature as stored in the Ledger.

- `ledgerMetadata` (dict):

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
        
- `stateMetadata` (dict):

    Metadata associated with the state (Patricia Merkle Trie) the returned transaction belongs to
    (see `ledgerId`).
    
    - `timestamp` (integer as POSIX timestamp):
     last update of the state
         
    - `poolRootHash` (base58-encoded hash string):
     pool state trie root hash to get the current state of the Pool
     (it can be used to get the state of the Pool at the moment the BLS multi-signature was created).
        
    - `rootHash` (base58-encoded string):
     state trie root hash for the ledger the returned transaction belongs to

- `poolMultiSignature` (dict):
 
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
    
- `metadata` (dict; optional):

    Metadata as in Request. It may be absent for Reply to write requests as `txn` fields already contains 
    this information as part of transaction written to the ledger.    

## Action Reply Structure

Each Reply to commands/actions follows the pattern as shown above.

```
{
    "from": <...>,
    "serialization": <...>,
    "msg": {
        "type": REPLY_COMMAND,
        "protocolVersion": <...>,
        
        "data": {
            "version": <...>,
            "type": <...>,
            
            "results": [
                "result": {
                    <result>
                },
            ]
        },
        "metadata": {
            "version": <...>,
            "reqId": <...>,
            "from": <...>,
        },
    }
}
```


## ACK Structure
Each ACK follows the pattern as shown above.

```
{
    "from": "GFAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": REQACK,
        "protocolVersion": 1,
        "data": {
            "version": 1,
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
    }
}
```


## NACK Structure
Each NACK follows the pattern as shown above.
```
{
    "from": "GFAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": REQNACK,
        "protocolVersion": <...>,
        "data": {
            "version": <...>,
            "reason": <reason_str>
        },
        "metadata": {
            "version": <...>,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

## Reject Structure
Each Reject follows the pattern as shown above.
```
{
    "from": "GFAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": REJECT,
        "protocolVersion": 1,
        "data": {
            "version": 1,
            "reason": <reason_str>
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
    }
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
    It differs from `from` metadata field, where `from` is the DID of the submitter.
    
    *Example*: `from` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
     
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
    Verkey can be changed to None by owner, it means that this user goes back under guardianship.

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
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 1,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "did": "N22KY2Dyvmuu2PyyqSFKue",
            "role": "101",
            "verkey": "~HmUWn928bnFT6Ephf65YXv"
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
    }
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 1,
        
            "results": [
                "result": {
                    "type": 1,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "N22KY2Dyvmuu2PyyqSFKue",
                        "role": "101",
                        "verkey": "~HmUWn928bnFT6Ephf65YXv"
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```

### ATTRIB

Adds attribute to a NYM record.

- `did` (base58-encoded string):

    Target DID we set an attribute for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `from` metadata field, where `from` is the DID of the submitter.
    
    *Example*: `from` is a DID of a Trust Anchor setting an attribute for a DID, and `did` is the DID we set an attribute for.
    
- `raw` (json; mutually exclusive with `hash` and `enc`):

    Raw data is represented as json, where key is attribute name and value is attribute value.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute data.

*Request Example*:
```
{
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 100,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "did": "N22KY2Dyvmuu2PyyqSFKue",
            "raw": "{"name": "Alice"}"
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    }
}
```

*Reply Example*:
```
{
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
        
            "results": [
                "result": {
                    "type": 100,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "N22KY2Dyvmuu2PyyqSFKue",
                        "raw": "{"name": "Alice"}"
                    },
                    
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
}
}
```


### SCHEMA
Adds Claim's schema.

It's not possible to update existing Schema.
So, if the Schema needs to be evolved, a new Schema with a new version or name needs to be created.

- `id` (string):

    Schema's ID as State Trie key (address or descriptive data). It must be unique within the ledger. 
    It must be equal (or be mapped to) the real key of the SCHEMA state in the State Trie. 

- `schemaName` (string):
 
    Schema's name string.

- `schemaVersion` (string):
 
    Schema's version string

- `value` (dict):

    Schema's specific data
    
    - `attrNames` (array of strings):
      Array of attribute name strings.
      
*Request Example*:
```
{
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 101,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "id":"L5AD5g65TDQr1PPHHRoiGf:Degree:1.0",
            "schemaVersion": "1.0",
            "schemaName": "Degree",
            "value": {
                "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
            }
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 101,
        
            "results": [
                "result": {
                    "type": 101,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "id":"L5AD5g65TDQr1PPHHRoiGf:Degree:1.0",
                        "schemaVersion": "1.0",
                        "schemaName": "Degree",
                        "value": {
                            "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
                        }
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```



### CLAIM_DEF
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema.

It's not possible to update `data` in existing Claim Def.
So, if a Claim Def needs to be evolved (for example, a key needs to be rotated), then
a new Claim Def needs to be created by a new Issuer DID (`did`).

- `id` (string):

    Schema's ID as State Trie key (address or descriptive data). It must be unique within the ledger. 
    It must be equal (or be mapped to) the real key of the SCHEMA state in the State Trie. 

- `type` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

- `tag` (string):

    A unique descriptive tag of the given CRED_DEF for the given Issuer and Schema. An Issuer may have multiple 
    CRED_DEFs for the same Schema created with different tags. 

- `schemaId` (string):
    
    ID of a Schema transaction the claim definition is created for.

- `value` (dict):

    Type-specific value:

    - `publicKeys` (dict):
     
         Dictionary with Claim Definition's public keys:
         
        - `primary`: primary claim public key
        - `revocation`: revocation claim public key


*Request Example*:
```
{
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 102,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "id":"HHAD5g65TDQr1PPHHRoiGf2L:5AD5g65TDQr1PPHHRoiGf:Degree:1.0:CL:key1",
            "signatureType": "CL",
            "schemaRef":"L5AD5g65TDQr1PPHHRoiGf1Degree1",
            "publicKeys": {
                "primary": ....,
                "revocation": ....
            },
            "tag": "key1",
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 102,
        
            "results": [
                "result": {
                    "type": 102,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "id":"HHAD5g65TDQr1PPHHRoiGf2L:5AD5g65TDQr1PPHHRoiGf:Degree:1.0:CL:key1",
                        "signatureType": "CL",
                        "schemaRef":"L5AD5g65TDQr1PPHHRoiGf1Degree1",
                        "publicKeys": {
                            "primary": ....,
                            "revocation": ....
                        },
                        "tag": "key1",
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```

### NODE
Adds a new node to the pool, or updates existing node in the pool.

- `did` (base58-encoded string):

    Target Node's DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `from` metadata field, where `from` is the DID of the transaction submitter (Steward"s DID).
    
    *Example*: `from` is a DID of a Steward creating a new Node, and `did` is the DID of this Node.
    
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
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 0,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "did": "6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8"
            "alias": "Node1",
            "clientIp": "127.0.0.1",
            "clientPort": 7588,
            "nodeIp": "127.0.0.1", 
            "nodePort": 7587,
            "blskey": "00000000000000000000000000000000",
            "services": ["VALIDATOR"]
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
        
            "results": [
                "result": {
                    "type": 0,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8"
                        "alias": "Node1",
                        "clientIp": "127.0.0.1",
                        "clientPort": 7588,
                        "nodeIp": "127.0.0.1", 
                        "nodePort": 7587,
                        "blskey": "00000000000000000000000000000000",
                        "services": ["VALIDATOR"]
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
                },
                 
                "ledgerMetadata": {
                    "ledgerId": 0, 
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
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
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 109,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "action": `start`,
            "version": `1.3`,
            "schedule": {"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
            "sha256": `db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55`,
            "force": false,
            "reinstall": false,
            "timeout": 1
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
        
            "results": [
                "result": {
                    "type": 109,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "action": `start`,
                        "version": `1.3`,
                        "schedule": {"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
                        "sha256": `db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55`,
                        "force": false,
                        "reinstall": false,
                        "timeout": 1
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
                },
                 
                "ledgerMetadata": {
                    "ledgerId": 2, 
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
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
    "from": "L5AD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "signature": {
        "type": "ED25519",
        "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
    },
    "msg": {
        "type": 111,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "writes":false,
            "force":true
        },
        
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        },
        "reqSignature": {
           "type": "ED25519",
           "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
        
            "results": [
                "result": {
                    "type": 111,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "writes":false,
                        "force":true
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                   "type": "ED25519",
                   "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
                },
                 
                "ledgerMetadata": {
                    "ledgerId": 2, 
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836443,
            "from": "L5AD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```

## Read Requests

### GET_NYM
Gets information about a DID (NYM).

- `did` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `from` metadata field, where `from` is the DID of the sender (may not exist on ledger at all).

*Request Example*:
```
{
    "from": "DDAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": 105,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "did": "N22KY2Dyvmuu2PyyqSFKue",
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 105,
        
            "results": [
                "result": {
                    "type": 1,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "N22KY2Dyvmuu2PyyqSFKue",
                        "role": "101",
                        "verkey": "~HmUWn928bnFT6Ephf65YXv"
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=",
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```


### GET_ATTRIB
Gets information about an Attribute for the specified DID.

NOTE: `GET_ATTRIB` for `hash` and `enc` attributes is something like the "proof of existence",
i.e. reply data contains requested value only.

- `did` (base58-encoded string):

    Target DID we get an attribute for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `from` metadata field, where `from` is the DID of the sender (may not exist on ledger at all).
    
- `raw` (string; mutually exclusive with `hash` and `enc`):

    Requested attribute name.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Requested attribute hash.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute. 

*Request Example*:
```
{
    "from": "DDAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": 104,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "did": "AH4RRiPR78DUrCWatnCW2w",
            "raw": "dateOfBirth"
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 104,
        
            "results": [
                "result": {
                    "type": 100,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "N22KY2Dyvmuu2PyyqSFKue",
                        "raw": "{"name": "Alice"}"
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=",
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        }
    } 
}
```

### GET_SCHEMA

Gets Claim's Schema.

- `id` (string):

    Schema's ID as State Trie key (address or descriptive data). It must be unique within the ledger. 
    It must be equal (or be mapped to) the real key of the SCHEMA state in the State Trie. 


*Request Example*:
```
{
    "from": "DDAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": 107,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "id":"L5AD5g65TDQr1PPHHRoiGf:Degree:1.0",
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 107,
        
            "results": [
                "result": {
                    "type": 101,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "id":"L5AD5g65TDQr1PPHHRoiGf:Degree:1.0",
                        "schemaVersion": "1.0",
                        "schemaName": "Degree",
                        "value": {
                            "attrNames": ["undergrad", "last_name", "first_name", "birth_date", "postgrad", "expiry_date"]
                        }
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=",
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        }
    }  
}
```
 
### GET_CLAIM_DEF

Gets Claim Definition.

- `id` (string):

    Schema's ID as State Trie key (address or descriptive data). It must be unique within the ledger. 
    It must be equal (or be mapped to) the real key of the SCHEMA state in the State Trie. 

*Request Example*:
```
{
    "from": "DDAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": 108,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "id":"HHAD5g65TDQr1PPHHRoiGf2L:5AD5g65TDQr1PPHHRoiGf:Degree:1.0:CL:key1",
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

*Reply Example*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 108,
        
            "results": [
                "result": {
                    "type": 102,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "id":"HHAD5g65TDQr1PPHHRoiGf2L:5AD5g65TDQr1PPHHRoiGf:Degree:1.0:CL:key1",
                        "signatureType": "CL",
                        "schemaRef":"L5AD5g65TDQr1PPHHRoiGf1Degree1",
                        "publicKeys": {
                            "primary": ....,
                            "revocation": ....
                        },
                        "tag": "key1",
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "state_proof": "+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=",
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        }
   }   
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
    "from": "DDAD5g65TDQr1PPHHRoiGf",
    "serialization": "MSG_PACK",
    "msg": {
        "type": 3,
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "ledgerId": "1",
            "seqNo": 9,
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        },
    }
}
```

*Reply Example (returns a NYM txn with seqNo=9)*:
```
{
    "from": "Node1",
    "serialization": "MSG_PACK",
    "msg": {
        "type": "REPLY",
        "protocolVersion": 1,
        
        "data": {
            "version": 1,
            "type": 108,
        
            "results": [
                "result": {
                    "type": 1,
                    "protocolVersion": 1,
                    
                    "data": {
                        "version": 1,
                        "did": "2VkbBskPNNyWrLrZq7DBhk",
                        "role": "101",
                        "verkey": "31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE"
                    },
                    "metadata": {
                        "version": 1,
                        "reqId": 1514215425836443,
                        "from": "L5AD5g65TDQr1PPHHRoiGf",
                    },
                },
                "txnMetadata": {
                    "version":1,
                    "creationTime": 1514211268,
                    "seqNo": 300,
                },
                "reqSignature": {
                    "type": "ED25519",
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
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
            
                "auditProof": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
            ]
        },
        "metadata": {
            "version": 1,
            "reqId": 1514215425836444,
            "from": "DDAD5g65TDQr1PPHHRoiGf",
        }
   }   
}
```
