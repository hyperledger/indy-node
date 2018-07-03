# Requests
* [Common Request Structure](#common-request-structure)
* [Reply Structure for Write Requests](#reply-structure-for-write-requests)
* [Reply Structure for Read Requests (except GET_TXN)](#reply-structure-for-read-requests)
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

* [Action Requests](#action-requests)

    * [POOL_RESTART](#pool_restrt)
    * [VALIDATOR_INFO](#validator_info)
    
This doc is about supported client's Request (both write and read ones).
If you are interested in transactions and their representation on the Ledger (that is internal one),
then have a look at [transactions](transactions.md).

[indy-sdk](https://github.com/hyperledger/indy-sdk) expects the format as specified below.

See [roles and permissions](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0) on the roles and who can create each type of transactions.

## Common Request Structure

Each Request (both write and read) is a JSON with a number of common metadata fields.

```
{
    'operation': {
        'type': '1',
        <request-specific fields>
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514215425836443,
    'protocolVersion': 1,
    'signature': '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd'
}
```

- `operation` (json):

    The request-specific operation json.
    
    - `type`: request type as one of the following values:

        - NODE = "0"
        - NYM = "1"
        - ATTRIB = "100"
        - SCHEMA = "101"
        - CLAIM_DEF = "102"
        - POOL_UPGRADE = "109"
        - NODE_UPGRADE = "110"
        - POOL_CONFIG = "111"
        - GET_TXN = "3"
        - GET_ATTR = "104"
        - GET_NYM = "105"
        - GET_SCHEMA = "107"
        - GET_CLAIM_DEF = "108"
        
    - request-specific data

- `identifier` (base58-encoded string):
 
     Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
     for 16 or 32 bit DID value.
     It may differ from `dest` field for some of requests (for example NYM), where `dest` is a 
     target identifier (for example, a newly created DID identifier).
     
     *Example*: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID.
     
- `reqId` (integer): 

    Unique ID number of the request with transaction.
    
- `protocolVersion` (integer; optional): 

    The version of client-to-node protocol. Each new version may introduce a new feature in Requests/Replies/Data.
    Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
    between clients and nodes.     
    
- `signature` (base58-encoded string; mutually exclusive with `signatures` field):
 
    Submitter's signature. Not required for read requests.
    
- `signatures` (map of base58-encoded string; mutually exclusive with `signature` field): 
    
    Submitters' signature in multisig case. This is a map where client's identifiers are the keys and 
    base58-encoded signature strings are the values. Not required for read requests.
    

Please find the format of each request-specific data for each type of request below.

## Reply Structure for Write Requests

Each Reply to write requests has a number of common metadata fields. Most of these fields are actually metadata fields 
of a transaction in the Ledger (see [transactions](transactions.md)).

```
{
    'op': 'REPLY', 
    'result': {
        "ver": <...>,
        "txn": {
            "type": <...>,
            "protocolVersion": <...>,
            
            "data": {
                "ver": <...>,
                <txn-specific fields>
            },
            
            "metadata": {
                "reqId": <...>,
                "from": <...>
            },
        },
        "txnMetadata": {
            "txnTime": <...>,
            "seqNo": <...>,  
            "txnId": <...>
        },
        "reqSignature": {
            "type": <...>,
            "values": [{
                "from": <...>,
                "value": <...>
            }]
        }
    
        'rootHash': '5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt'],
    }
}
```
- `ver` (string):

    Transaction version to be able to evolve content.
    The content of all sub-fields may depend on the version.       

- `txn` (dict):
    
    Transaction-specific payload (data)

    - `type` (enum number as string):
    
        Supported transaction type:
        
        - NODE = 0
        - NYM = 1
        - ATTRIB = 100
        - SCHEMA = 101
        - CLAIM_DEF = 102
        - POOL_UPGRADE = 109
        - NODE_UPGRADE = 110
        - POOL_CONFIG = 111

    - `protocolVersion` (integer; optional): 
    
        The version of client-to-node or node-to-node protocol. Each new version may introduce a new feature in Requests/Replies/Data.
        Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
        between clients and nodes.     
     
    - `data` (dict):

        Transaction-specific data fields (see next sections for each transaction description).  
       
    - `metadata` (dict):
    
        Metadata as came from the Request.

        - `from` (base58-encoded string):
             Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
             for 16 or 32 byte DID value.
             It may differ from `did` field for some of transaction (for example NYM), where `did` is a 
             target identifier (for example, a newly created DID identifier).
             
             *Example*: `from` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
             
        - `reqId` (integer): 
            Unique ID number of the request with transaction.
  
- `txnMetadata` (dict):

    Metadata attached to the transaction.
    
    - `txnTime` (integer as POSIX timestamp):
        The time when transaction was written to the Ledger as POSIX timestamp.
        
    - `seqNo` (integer):
        A unique sequence number of the transaction on Ledger
        
    - `txnId` (string):
        Txn ID as State Trie key (address or descriptive data). It must be unique within the ledger.
  
- `reqSignature` (dict):

    Submitter's signature over request with transaction (`txn` field).
    
    - `type` (string enum):
        
        - ED25519: ed25519 signature
        - ED25519_MULTI: ed25519 signature in multisig case.
    
    - `values` (list): 
        
        - `from` (base58-encoded string):
        Identifier (DID) of signer as base58-encoded string for 16 or 32 byte DID value.
        
        - `value` (base58-encoded string):
         signature value
         
- `rootHash` (base58-encoded hash string):

    base58-encoded ledger's merkle tree root hash
    
- `auditPath` (array of base58-encoded hash strings):

    ledger's merkle tree audit proof as array of base58-encoded hash strings
    (this is a cryptographic proof to verify that the new transaction has 
    been appended to the ledger)
    
- transaction-specific fields as defined in [transactions](transactions.md) for each transaction type

## Reply Structure for Read Requests

The structure below is not applicable for [GET_TXN](#get_txn).

Each Reply to read requests has a number of common metadata fields and state-proof related fields.
Some of these fields are actually metadata fields of a transaction in the Ledger (see [transactions](transactions.md)).

These common metadata values are added to result's JSON at the same level as real data.

**TODO**: consider distinguishing and separating real transaction data and metadata into different levels.


```
{
    'op': 'REPLY', 
    'result': {
        'type': '105',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514214863899317,
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'state_proof': {
            'root_hash': '7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514214795,
                    'ledger_id': 1, 
                    'txn_root_hash': 'DqQ7G4fgDHBfdfVLrE6DCdYyyED1fY5oKw76aDeFsLVr',
                    'pool_state_root_hash': 'TfMhX3KDjrqq94Wj7BHV9sZrgivZyjbHJ3cGRG4h1Zj',
                    'state_root_hash': '7Wdj3rrMCZ1R1M78H4xK5jxikmdUUGW2kbfJQ1HoEpK'
                },
                'signature': 'RTyxbErBLcmTHBLj1rYCAEpMMkLnL65kchGni2tQczqzomYWZx9QQpLvnvNN5rD2nXkqaVW3USGak1vyAgvj2ecAKXQZXwcfosmnsBvRrH3M2M7cJeZSVWJCACfxMWuxAoMRtuaE2ABuDz6NFcUctXcSa4rdZFkxh5GoLYFqU4og6b',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
        'data': <transaction-specific data>,
        
        <request-specific data>
}
```


- `type` (enum number as string): 

    Supported transaction types:
    
    - GET_ATTR = "104"
    - GET_NYM = "105"
    - GET_SCHEMA = "107"
    - GET_CLAIM_DEF = "108"

- `identifier` (base58-encoded string):
 
     as was in read Request (may differ from the `identifier` in `data` which defines 
     transaction submitter)
     
- `reqId` (integer): 

    as was in read Request (may differ from the `reqId` in `data` which defines 
    the request used to write the transaction to the Ledger)
    
- `seqNo` (integer):

    a unique sequence number of the transaction on Ledger

- `txnTime` (integer as POSIX timestamp): 

    the time when transaction was written to the Ledger as POSIX timestamp
    
- `state_proof` (dict):

    State proof with BLS multi-signature of the State:
    
    - `root_hash` (base58-encoded string): state trie root hash for the ledger the returned transaction belongs to
    - `proof_nodes` (base64-encoded string): state proof for the returned transaction against the state trie with the specified `root_hash`
    - `multi_signature` (dict): BLS multi-signature against the specified state trie root hash
        - `value` (dict): the value the BLS multi-signature was created against
            - `timestamp` (integer as POSIX timestamp): last update of the state
            - `ledger_id` (integer enum): ID of the ledger the returned transaction belongs to (Pool=0; Domain=1; Config=2)
            - `txn_root_hash` (base58-encoded string): root hash of the ledger the returned transaction belongs to
            - `state_root_hash` (base58-encoded string): state trie root hash for the ledger the returned transaction belongs to
            - `pool_state_root_hash` (base58-encoded string): pool state trie root hash to get the state of the Pool at the moment the BLS multi-signature was created
        - `signature` (base58-encoded string): BLS multi-signature against the state trie with the specified `root_hash`
        - `participants` (array os strings): Aliases of Nodes participated in BLS multi-signature (the number of participated nodes is not less than n-f)
            
- `data` (json or dict):

    transaction-specific data (see [transactions](transactions.md) for each transaction type)
    
- request-specific fields as they appear in Read request      
    
      
## Write Requests

The format of each request-specific data for each type of request.

### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and trustee can be created only by other trusties (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).

The request can be used for 
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID.
     
- `role` (enum number as string; optional): 

    Role of a user NYM record being created for. One of the following numbers
    
    - None (common USER)
    - "0" (TRUSTEE)
    - "2" (STEWARD)
    - "101" (TRUST_ANCHOR)
    
  A TRUSTEE can change any Nym's role to None, this stopping it from making any writes (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).
  
- `verkey` (base58-encoded string, possibly starting with "~"; optional):

    Target verification key as base58-encoded string. It can start with "~", which means that
    it's abbreviated verkey and should be 16 bytes long when decoded, otherwise it's a full verkey
    which should be 32 bytes long when decoded. If not set, then either the target identifier
    (`dest`) is 32-bit cryptonym CID (this is deprecated), or this is a user under guardianship
    (doesnt owns the identifier yet).
    Verkey can be changed to None by owner, it means that this user goes back under guardianship.

- `alias` (string; optional): 

    NYM's alias.
    

If there is no NYM transaction with the specified DID (`dest`), then it can be considered as creation of a new DID.

If there is a NYM transaction with the specified DID (`dest`),  then this is update of existing DID.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if key rotation needs to be performed, the owner of the DID needs to send a NYM request with
`dest` and `verkey` only. `role` and `alias` will stay the same.


*Request Example*:
```
{
    'operation': {
        'type': '1'
        'dest': 'GEzcdDLhCpGCYRHW82kjHd',
        'role': '101',
        'verkey': '~HmUWn928bnFT6Ephf65YXv'
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514213797569745,
    'protocolVersion': 1,
    'signature': '49W5WP5jr7x1fZhtpAhHFbuUDqUYZ3AKht88gUjrz8TEJZr5MZUPjskpfBFdboLPZXKjbGjutoVascfKiMD5W7Ba',
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":"1",
            "protocolVersion":1,
            
            "data": {
                "ver": 1,
                "dest":"GEzcdDLhCpGCYRHW82kjHd",
                "verkey":"~HmUWn928bnFT6Ephf65YXv",
                "role":101,
            },
            
            "metadata": {
                "reqId":1514213797569745,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,
            "txnId": "N22KY2Dyvmuu2PyyqSFKue|01"
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "49W5WP5jr7x1fZhtpAhHFbuUDqUYZ3AKht88gUjrz8TEJZr5MZUPjskpfBFdboLPZXKjbGjutoVascfKiMD5W7Ba"
            }]
        }
		
        'rootHash': '5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt'],
		
        'dest': 'N22KY2Dyvmuu2PyyqSFKue',
        'role': '101',
        'verkey': '31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE'
    }
}
```

### ATTRIB

Adds attribute to a NYM record.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of a Trust Anchor setting an attribute for a DID, and `dest` is the DID we set an attribute for.
    
- `raw` (json; mutually exclusive with `hash` and `enc`):

    Raw data is represented as json, where key is attribute name and value is attribute value.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute data.

*Request Example*:
```
{
    'operation': {
        'type': '100'
        'dest': 'N22KY2Dyvmuu2PyyqSFKue',
        'raw': '{"name": "Alice"}'
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514213797569745,
    'protocolVersion': 1,
    'signature': '49W5WP5jr7x1fZhtpAhHFbuUDqUYZ3AKht88gUjrz8TEJZr5MZUPjskpfBFdboLPZXKjbGjutoVascfKiMD5W7Ba',
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":"100",
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                "dest":"N22KY2Dyvmuu2PyyqSFKue",
                'raw': '{"name":"Alice"}'
            },
            
            "metadata": {
                "reqId":1514213797569745,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId": "N22KY2Dyvmuu2PyyqSFKue|02"
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "49W5WP5jr7x1fZhtpAhHFbuUDqUYZ3AKht88gUjrz8TEJZr5MZUPjskpfBFdboLPZXKjbGjutoVascfKiMD5W7Ba"
            }]
        }    
    
        'rootHash': '5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt'],
		
    }
}
```

### SCHEMA
Adds Claim's schema.

It's not possible to update existing Schema.
So, if the Schema needs to be evolved, a new Schema with a new version or name needs to be created.

- `data` (dict):
 
     Dictionary with Schema's data:
     
    - `attr_names`: array of attribute name strings
    - `name`: Schema's name string
    - `version`: Schema's version string

*Request Example*:
```
{
    'operation': {
        'type': '101',
        'data': {
            'version': '1.0',
            'name': 'Degree',
            'attr_names': ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad', 'expiry_date']
        },
    },

    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 1,
    'signature': '5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS'
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":"101",
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                "data": {
                    "name": "Degree",
                    "version": "1.0",
                    'attr_names': ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad', 'expiry_date']
                }
            },
            
            "metadata": {
                "reqId":1514280215504647,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"L5AD5g65TDQr1PPHHRoiGf1|Degree|1.0",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS"
            }]
        }
 		
        'rootHash': '5vasvo2NUAD7Gq8RVxJZg1s9F7cBpuem1VgHKaFP8oBm',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '66BCs5tG7qnfK6egnDsvcx2VSNH6z1Mfo9WmhLSExS6b'],
		
    }
}
```

### CLAIM_DEF
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema.

It's not possible to update `data` in existing Claim Def.
So, if a Claim Def needs to be evolved (for example, a key needs to be rotated), then
a new Claim Def needs to be created by a new Issuer DID (`identifier`).


- `data` (dict):
 
     Dictionary with Claim Definition's data:
     
    - `primary` (dict): primary claim public key
    - `revocation` (dict): revocation claim public key
        
- `ref` (string):
    
    Sequence number of a Schema transaction the claim definition is created for.

- `signature_type` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

- `tag` (string, optional):

    A unique tag to have multiple public keys for the same Schema and type issued by the same DID.
    A default tag `tag` will be used if not specified. 

*Request Example*:
```
{
    'operation': {
        'type': '102',
        'signature_type': 'CL',
        'ref': 10,
        'tag': 'some_tag',    
        'data': {
            'primary': ....,
            'revocation': ....
        }
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 1,
    'signature': '5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS'
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":"102",
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                "signature_type":"CL",
                'ref': 10,    
                'tag': 'some_tag',
                'data': {
                    'primary': ....,
                    'revocation': ....
                }
            },
            
            "metadata": {
                "reqId":1514280215504647,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1|Degree1|CL|key1",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS"
            }]
        }
    }
}
```

### NODE
Adds a new node to the pool, or updates existing node in the pool.

- `data` (dict):
    
    Data associated with the Node:
    
    - `alias` (string): Node's alias
    - `blskey` (base58-encoded string; optional): BLS multi-signature key as base58-encoded string (it's needed for BLS signatures and state proofs support)
    - `client_ip` (string; optional): Node's client listener IP address, that is the IP clients use to connect to the node when sending read and write requests (ZMQ with TCP)  
    - `client_port` (string; optional): Node's client listener port, that is the port clients use to connect to the node when sending read and write requests (ZMQ with TCP)
    - `node_ip` (string; optional): The IP address other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `node_port` (string; optional): The port other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `services` (array of strings; optional): the service of the Node. `VALIDATOR` is the only supported one now. 

- `dest` (base58-encoded string):

    Target Node's DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the transaction submitter (Steward's DID).
    
    *Example*: `identifier` is a DID of a Steward creating a new Node, and `dest` is the DID of this Node.
    
- `verkey` (base58-encoded string, possibly starting with "~"; optional):

    Target Node verification key as base58-encoded string.
    It may absent if `dest` is 32-bit cryptonym CID. 

If there is no NODE transaction with the specified Node ID (`dest`), then it can be considered as creation of a new NODE.

If there is a NODE transaction with the specified Node ID (`dest`), then this is update of existing NODE.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if a Steward wants to rotate BLS key, then it's sufficient to send a NODE transaction with `dest` and a new `blskey` in `data`.
There is no need to specify all other fields in `data`, and they will remain the same.

*Request Example*:
```
{
    'operation': {
        'type': '0'
     	'data': {
     		'alias': 'Node1',
     		'client_ip': '127.0.0.1',
     		'client_port': 7588,
     		'node_ip': '127.0.0.1', 
     		'node_port': 7587,
     		'blskey': '00000000000000000000000000000000',
     		'services': ['VALIDATOR']}
     	} ,
     	'dest': '6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8'
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 1,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj',
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":0,
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                'data': {
                    'alias': 'Node1',
                    'client_ip': '127.0.0.1',
                    'client_port': 7588,
                    'node_ip': '127.0.0.1', 
                    'node_port': 7587,
                    'blskey': '00000000000000000000000000000000',
                    'services': ['VALIDATOR']}
                } ,
                'dest': '6HoV7DUEfNDiUP4ENnSC4yePja8w7JDQJ5uzVgyW4nL8'
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"Delta",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "21BPzYYrFzbuECcBV3M1FH",
                "value": "3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj"
            }]
        }
 		
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
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
    'operation': {
        'type': '109'
        'name': `upgrade-13`,
        'action': `start`,
        'version': `1.3`,
        'schedule': {"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
        'sha256': `db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55`,
        'force': false,
        'reinstall': false,
        'timeout': 1
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 1,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj',
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver": 1,
        "txn": {
            "type":109,
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                "name":"upgrade-13",
                "action":"start",
                "version":"1.3",
                "schedule":{"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
                "sha256":"db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55",
                "force":false,
                "reinstall":false,
                "timeout":1,
                "justification":null,
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "txnId":"upgrade-13",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "21BPzYYrFzbuECcBV3M1FH",
                "value": "3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj"
            }]
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
    'operation': {
        'type': '111'
        'writes':false,
        'force':true
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 1,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj',
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver":1,
        "txn": {
            "type":111,
            "protocolVersion":1,
            
            "data": {
                "ver":1,
                "writes":false,
                "force":true,
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"1111",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "21BPzYYrFzbuECcBV3M1FH",
                "value": "3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj"
            }]
        }
    }
}
```

## Read Requests

### GET_NYM
Gets information about a DID (NYM).

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of the read request sender, and `dest` is the requested DID.

*Request Example*:
```
{
    'operation': {
        'type': '105'
        'dest': '2VkbBskPNNyWrLrZq7DBhk'
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 1
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '105',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 1, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
        'data': '{"dest":"2VkbBskPNNyWrLrZq7DBhk","identifier":"L5AD5g65TDQr1PPHHRoiGf","role":null,"seqNo":10,"txnTime":1514308168,"verkey":"~6hAzy6ubo3qutnnw5A12RF"}',
        
        'dest': '2VkbBskPNNyWrLrZq7DBhk'
    }
}
```

### GET_ATTRIB
Gets information about an Attribute for the specified DID.

NOTE: `GET_ATTRIB` for `hash` and `enc` attributes is something like the "proof of existence",
i.e. reply data contains requested value only.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of read request sender, and `dest` is the DID we get an attribute for.
    
- `raw` (string; mutually exclusive with `hash` and `enc`):

    Requested attribute name.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Requested attribute hash.

- `enc` (string; mutually exclusive with `raw` and `hash`):

    Encrypted attribute. 

*Request Example*:
```
{
    'operation': {
        'type': '104'
        'dest': 'AH4RRiPR78DUrCWatnCW2w',
        'raw': 'dateOfBirth'
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 1
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '104',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 1, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
        'data': '{"dateOfBirth":{"dayOfMonth":23,"month":5,"year":1984}}',
        
        'dest': 'AH4RRiPR78DUrCWatnCW2w',
        'raw': 'dateOfBirth'
    }
}
```

### GET_SCHEMA

Gets Claim's Schema.

- `dest` (base58-encoded string):

    Schema Issuer's DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of the read request sender, and `dest` is the DID of the Schema's Issuer.

- `data` (dict):

    - `name` (string):  Schema's name string
    - `version` (string): Schema's version string
    

 
*Request Example*:
```
{
    'operation': {
        'type': '107'
        'dest': '2VkbBskPNNyWrLrZq7DBhk',
        'data': {
            'name': 'Degree',
             'version': '1.0'
        },
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 1
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '107',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 1, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
        'data': {
            'name': 'Degree',
            'version': '1.0',
            'attr_names': ['attrib1', 'attrib2', 'attrib3']
        }, 
        
        'dest': '2VkbBskPNNyWrLrZq7DBhk'
    }
}
```

### GET_CLAIM_DEF

Gets Claim Definition.

- `origin` (base58-encoded string):

    Claim Definition Issuer's DID as base58-encoded string for 16 or 32 byte DID value.
        
- `ref` (string):
    
    Sequence number of a Schema transaction the claim definition is created for.

- `signature_type` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

- `tag` (string, optional):

    A unique tag to have multiple public keys for the same Schema and type issued by the same DID.
    A default tag `tag` will be used if not specified. 

*Request Example*:
```
{
    'operation': {
        'type': '108'
        'signature_type': 'CL',
        'origin': '2VkbBskPNNyWrLrZq7DBhk',
        'ref': 10,
        'tag': 'some_tag',
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 1
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '108',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'seqNo': 10,

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 1, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
        'data': {
            'primary': ...,
            'revocation': ...
        },
        
        'signature_type': 'CL',
        'origin': '2VkbBskPNNyWrLrZq7DBhk',
        'ref': 10,
        'tag': 'some_tag'
    }
}
```

### GET_TXN

A generic request to get a transaction from Ledger by its sequence number.

- `ledgerId` (int enum):

    ID of the ledger the requested transaction belongs to (Pool=0; Domain=1; Config=2).

- `data` (int):

    Requested transaction sequence number as it's stored on Ledger.

*Request Example (requests a NYM txn with seqNo=9)*:
```
{
    'operation': {
        'type': '3',
        'ledgerId': 1,
        'data': 9
    },
    
    'identifier': 'MSjKTWkPLtYoPEaTF1TUDb',
    'reqId': 1514311281279625,
    'protocolVersion': 1
}
```

*Reply Example (returns requested NYM txn with seqNo=9)*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '3',
        'identifier': 'MSjKTWkPLtYoPEaTF1TUDb',
        'reqId': 1514311352551755,
       
        'seqNo': 9,

        'data': {
            'type': '1',
            'identifier': 'MSjKTWkPLtYoPEaTF1TUDb',
            'reqId': 1514311345476031,
            'signature': '4qDmMAGqjzr4nh7S3rzLX3V9iQYkHurrYvbibHSvQaKw3u3BouTdLwv6ZzzavAjS635kAqpj5kKG1ehixTUkzFjK',
            'signatures': None,
            
            'seqNo': 9,
            `txnTime': 1514311348,
            
            'rootHash': '5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn',
            'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt'],
            
            'alias': 'name',
            'dest': 'WTJ1xmQViyFb67WAuvPnJP',
            'role': '2',
            'verkey': '~HjhFpNnFJKyceyELpCz3b5'
        }
    }
}
```


## Action Requests

### POOL_RESTART
The command to restart all nodes at the time specified in field "datetime"(sent by Trustee).

- `datetime` (string):

    Restart time in datetime frmat/
    To restart as early as possible, send message without the "datetime" field or put in it value "0" or ""(empty string) or the past date on this place.
    The restart is performed immediately and there is no guarantee of receiving an answer with Reply.


- `action` (enum: `start` or `cancel`):

    Starts or cancels the Restart.

*Request Example*:
```
{
    "reqId": 98262,
    "signature": "cNAkmqSySHTckJg5rhtdyda3z1fQcV6ZVo1rvcd8mKmm7Fn4hnRChebts1ur7rGPrXeF1Q3B9N7PATYzwQNzdZZ",
    "protocolVersion": 1,
    "identifier": "M9BJDuS24bqbJNvBRsoGg3",
    "operation": {
            "datetime": "2018-03-29T15:38:34.464106+00:00",
            "action": "start",
            "type": "118"
    }
}
```

*Reply Example*:
```
{
    "op": "REPLY",
    "result": {
            "reqId": 98262,
            "type": "118",
            "identifier": "M9BJDuS24bqbJNvBRsoGg3",
            "datetime": "2018-03-29T15:38:34.464106+00:00",
            "action": "start",
    }
}
```

### VALIDATOR_INFO
Command provide info from all the connected nodes without need of consensus.

*Request Example*:
```
{
    'protocolVersion': 1,
    'reqId': 83193,
    'identifier': 'M9BJDuS24bqbJNvBRsoGg3',
    'operation': {
                'type': '119'
    }
}
```

*Reply Example*:
```
{
    'op': 'REPLY',
    'result': {
            'reqId': 83193,
            'data': { <Json with node info> },
            'type': '119',
            'identifier': 'M9BJDuS24bqbJNvBRsoGg3'
    }
}
```
