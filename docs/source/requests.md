# Requests
* [Common Request Structure](#common-request-structure)
* [Reply Structure for Write Requests](#reply-structure-for-write-requests)
* [Reply Structure for Read Requests (except GET_TXN)](#reply-structure-for-read-requests)
* [Write Requests](#write-requests)

    * [NYM](#nym)    
    * [ATTRIB](#attrib)    
    * [SCHEMA](#schema)
    * [CLAIM_DEF](#claim_def)
    * [REVOC_REG_DEF](#revoc_reg_def)
    * [REVOC_REG_ENTRY](#revoc_reg_entry)
    * [NODE](#node)
    * [POOL_UPGRADE](#pool_upgrade)
    * [POOL_CONFIG](#pool_config)
    * [AUTH_RULE](#auth_rule)
    * [AUTH_RULES](#auth_rules)
    * [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)
    * [TRANSACTION_AUTHOR_AGREEMENT_AML](#transaction_author_agreement_AML)    
    * [TRANSACTION_AUTHOR_AGREEMENT_DISABLE](#transaction_author_agreement_disable)
    * [SET_CONTEXT](#set_context)

* [Read Requests](#read-requests)

    * [GET_NYM](#get_nym)    
    * [GET_ATTRIB](#get_attrib)    
    * [GET_SCHEMA](#get_schema)
    * [GET_CLAIM_DEF](#get_claim_def)
    * [GET_REVOC_REG_DEF](#get_revoc_reg_def)
    * [GET_REVOC_REG](#get_revoc_reg)
    * [GET_REVOC_REG_DELTA](#get_revoc_reg_delta)    
    * [GET_AUTH_RULE](#get_auth_rule)
    * [GET_TRANSACTION_AUTHOR_AGREEMENT](#get_transaction_author_agreement)
    * [GET_TRANSACTION_AUTHOR_AGREEMENT_AML](#get_transaction_author_agreement_aml)
    * [GET_CONTEXT](#get_context)
    * [GET_TXN](#get_txn)

* [Action Requests](#action-requests)

    * [POOL_RESTART](#pool_restart)
    * [VALIDATOR_INFO](#validator_info)
    
This doc is about supported client's Request (both write and read ones).
If you are interested in transactions and their representation on the Ledger (that is internal one),
then have a look at [transactions](transactions.md).

[indy-sdk](https://github.com/hyperledger/indy-sdk) expects the format as specified below.

See [roles and permissions](https://github.com/hyperledger/indy-node/blob/master/docs/source/auth_rules.md) on the roles and who can create each type of transactions.

## Common Request Structure

Each Request (both write and read) is a JSON with a number of common metadata fields.

```
{
    'operation': {
        'type': <request type>,
        <request-specific fields>
    },
    
    'identifier': <author DID>,
    `endorser`: <endorser DID>, 
    'reqId': <req_id unique integer>,
    'protocolVersion': 2,
    'signature': <signature_value>,
    # 'signatures': {
    #      `did1`: <sig1>,
    #      `did2`: <sig2>,
    #  }    
           
}
```

- `operation` (json):

    The request-specific operation json.
    
    - `type`: request type as one of the following values:
        
        - write requests (transactions):

            - NODE = "0"
            - NYM = "1"
            - TXN_AUTHOR_AGREEMENT = "4"
            - TXN_AUTHOR_AGREEMENT_AML = "5"
            - ATTRIB = "100"
            - SCHEMA = "101"
            - CLAIM_DEF = "102"
            - POOL_UPGRADE = "109"
            - NODE_UPGRADE = "110"
            - POOL_CONFIG = "111"
            - REVOC_REG_DEF = "113"
            - REVOC_REG_ENTRY = "114"
            - AUTH_RULE = "120"
            - AUTH_RULES = "122"
            - SET_CONTEXT = "200"
            
        - read requests:
        
            - GET_TXN = "3"
            - GET_TXN_AUTHOR_AGREEMENT = "6"
            - GET_TXN_AUTHOR_AGREEMENT_AML = "7"        
            - GET_ATTR = "104"
            - GET_NYM = "105"
            - GET_SCHEMA = "107"
            - GET_CLAIM_DEF = "108"
            - GET_REVOC_REG_DEF = "115"
            - GET_REVOC_REG = "116"
            - GET_REVOC_REG_DELTA = "117"  
            - GET_AUTH_RULE = "121"      
            - GET_CONTEXT = "300"
            
    - request-specific data

- `identifier` (base58-encoded string):
    
     Identifier of the transaction author as base58-encoded string
     for 16 or 32 bit DID value.
 
     For read requests this is read request submitter. It can be any DID (not necessary present on the ledger as a NYM txn)
 
     For write requests this is transaction author.
     It may differ from `endorser` field who submits the transaction on behalf of `identifier`. If `endorser` is absent,
     then the author (`identifier`) plays the role of endorser and submits request by his own.
     It also may differ from `dest` field for some of requests (for example NYM), where `dest` is a 
     target identifier (for example, a newly created DID identifier).
     
     *Example*:
     
     - `identifier` is a DID of a transaction author who doesn't have write permissions; `endorser` is a DID of a user with Endorser role (that is with write permissions).
     - new NYM creation: `identifier` is a DID of an Endorser creating a new DID, and `dest` is a newly created DID.
 
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

## Common Write Request Structure

Write requests to Domain and added-by-plugins ledgers may have additional Transaction Author Agreement acceptance fields:

```
{
    'operation': {
        'type': <request type>,
        <request-specific fields>
    },
    
    'identifier': <author DID>,
    'endorser': <endorser DID>,
    'reqId': <req_id unique integer>,
    'taaAcceptance': {
        'taaDigest': <digest hex string>,
        'mechanism': <mechaism string>,
        'time': <time integer>
     }
    'protocolVersion': 2,
    'signature': <signature_value>,
    # 'signatures': {
    #      `did1`: <sig1>,
    #      `did2`: <sig2>,
    #  }    
           
}
```

Additional (optional) fields for write requests:

- `endorser` (base58-encoded string, optional):
    Identifier (DID) of an Endorser submitting a transaction on behalf of the original author (`identifier`) as base58-encoded string for 16 or 32 bit DID value.
   If `endorser` is absent, then the author (`identifier`) plays the role of endorser and submits request by his own. 
   If `endorser` is present then the transaction must be multi-signed by the both author (`identifier`) and Endorser (`endorser`).  

- `taaAcceptance` (dict, optional):
            If transaction author agreement is set/enabled, then every transaction (write request) from Domain and plugins-added ledgers must include acceptance of the latest transaction author agreement.
            
   - `taaDigest` (SHA256 hex digest string): SHA256 hex digest of the latest Transaction Author Agreement on the ledger. The digest is calculated from concatenation of [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)'s `version` and `text`.
                
   - `mechanism` (string): a mechanism used to accept the signature; must be present in the latest list of transaction author agreement acceptane mechanisms on the ledger  
                
   - `time` (integer as POSIX timestamp): transaction author agreement acceptance time
                
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
                "from": <...>,
                "endorser": <...>,
                "digest": <...>,
                "payloadDigest": <...>,
                "taaAcceptance": {
                    "taaDigest": <...>,
                    "mechanism": <...>,
                    "time": <...>
                 }
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
        
        - NODE = "0"
        - NYM = "1"
        - TXN_AUTHOR_AGREEMENT = "4"
        - TXN_AUTHOR_AGREEMENT_AML = "5"
        - ATTRIB = "100"
        - SCHEMA = "101"
        - CLAIM_DEF = "102"
        - POOL_UPGRADE = "109"
        - NODE_UPGRADE = "110"
        - POOL_CONFIG = "111"
        - REVOC_REG_DEF = "113"
        - REVOC_REG_DEF = "114"
        - AUTH_RULE = "120"
        - SET_CONTEXT = "200"

    - `protocolVersion` (integer; optional): 
    
        The version of client-to-node or node-to-node protocol. Each new version may introduce a new feature in Requests/Replies/Data.
        Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
        between clients and nodes.     
     
    - `data` (dict):

        Transaction-specific data fields (see next sections for each transaction description).  
       
    - `metadata` (dict):
    
        Metadata as came from the Request.

        - `from` (base58-encoded string):
             Identifier (DID) of the transaction author as base58-encoded string
             for 16 or 32 bit DID value.
             It may differ from `endorser` field who submits the transaction on behalf of `identifier`.
             If `endorser` is absent, then the author (`identifier`) plays the role of endorser and submits request by his own.
             It also may differ from `dest` field for some of requests (for example NYM), where `dest` is a 
             target identifier (for example, a newly created DID identifier).
             
             *Example*:
             
             - `identifier` is a DID of a transaction author who doesn't have write permissions; `endorser` is a DID of a user with Endorser role (that is with write permissions).
             - new NYM creation: `identifier` is a DID of an Endorser creating a new DID, and `dest` is a newly created DID.
        - `reqId` (integer): 
            Unique ID number of the request with transaction.
  
        - `digest` (SHA256 hex digest string):
            SHA256 hash hex digest of all fields in the initial requests (including signatures) 
            
        - `payloadDigest` (SHA256 hex digest string):
            SHA256 hash hex digest of the payload fields in the initial requests, that is all fields excluding signatures and plugins-added ones
            
        - `endorser` (base58-encoded string, optional):
            Identifier (DID) of an Endorser submitting a transaction on behalf of the original author (`identifier`) as base58-encoded string for 16 or 32 bit DID value.
            If `endorser` is absent, then the author (`identifier`) plays the role of endorser and submits request by his own. 
            If `endorser` is present then the transaction must be multi-signed by the both author (`identifier`) and Endorser (`endorser`). 
                        
        - `taaAcceptance` (dict, optional):
            If transaction author agreement is set/enabled, then every transaction (write request) from Domain and plugins-added ledgers must include acceptance of the latest transaction author agreement.
            
                - `taaDigest` (SHA256 hex digest string): SHA256 hex digest of the latest Transaction Author Agreement on the ledger
                
                - `mechanism` (string): a mechanism used to accept the signature; must be present in the latest list of transaction author agreement acceptane mechanisms on the ledger  
                
                - `time` (integer as POSIX timestamp): transaction author agreement acceptance time. The time needs to be rounded to date to prevent correlation of different transactions which is possible when acceptance time is too precise.
                  
  
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
    
    - GET_TXN = "3"
    - GET_TXN_AUTHOR_AGREEMENT = "6"
    - GET_TXN_AUTHOR_AGREEMENT_AML = "7"        
    - GET_ATTR = "104"
    - GET_NYM = "105"
    - GET_SCHEMA = "107"
    - GET_CLAIM_DEF = "108"
    - GET_REVOC_REG_DEF = "115"
    - GET_REVOC_REG = "116"
    - GET_REVOC_REG_DELTA = "117"  
    - GET_AUTH_RULE = "121"    
    - GET_CONTEXT = "300"

- `identifier` (base58-encoded string):
 
     read request submitter's DID as was in read Request (may differ from the `identifier` in `data` which defines transaction author)
     
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
Creates a new NYM record for a specific user, endorser, steward or trustee.
Note that only trustees and stewards can create new endorsers and trustee can be created only by other trusties (see [roles](https://github.com/hyperledger/indy-node/blob/master/docs/source/auth_rules.md)).

The request can be used for 
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It may differ from `identifier` metadata field, where `identifier` is the DID of the submitter.
    If they are equal (in permissionless case), then transaction must be signed by the newly created `verkey`.
    
    *Example*: `identifier` is a DID of a Endorser creating a new DID, and `dest` is a newly created DID.
     
- `role` (enum number as string; optional): 

    Role of a user NYM record being created for. One of the following numbers
    
    - None (common USER)
    - "0" (TRUSTEE)
    - "2" (STEWARD)
    - "101" (ENDORSER)
    - "201" (NETWORK_MONITOR)
    
  A TRUSTEE can change any Nym's role to None, this stopping it from making any writes (see [roles](https://github.com/hyperledger/indy-node/blob/master/docs/source/auth_rules.md)).
  
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
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
            "data": {
                "ver": 1,
                "dest":"GEzcdDLhCpGCYRHW82kjHd",
                "verkey":"~HmUWn928bnFT6Ephf65YXv",
                "role":101,
            },
            
            "metadata": {
                "reqId":1514213797569745,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
    
    *Example*: `identifier` is a DID of a Endorser setting an attribute for a DID, and `dest` is the DID we set an attribute for.
    
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
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                "dest":"N22KY2Dyvmuu2PyyqSFKue",
                'raw': '{"name":"Alice"}'
            },
            
            "metadata": {
                "reqId":1514213797569745,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
     
    - `attr_names`: array of attribute name strings (125 attributes maximum)
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
    'endorser': 'D6HG5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
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
                "endorser": "D6HG5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
    'endorser': 'D6HG5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
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
                "endorser": "D6HG5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
        },
        
        'rootHash': '5vasvo2NUAD7Gq8RVxJZg1s9F7cBpuem1VgHKaFP8oBm',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '66BCs5tG7qnfK6egnDsvcx2VSNH6z1Mfo9WmhLSExS6b'],
        
    }
}
```

### REVOC_REG_DEF
Adds a Revocation Registry Definition, that Issuer creates and publishes for a particular Claim Definition.
It contains public keys, maximum number of credentials the registry may contain, reference to the Claim Def, plus some revocation registry specific data.

- `value` (dict):

     Dictionary with revocation registry definition's data:
     
     - `maxCredNum` (integer): a maximum number of credentials the Revocation Registry can handle
     - `tailsHash` (string): tails' file digest
     - `tailsLocation` (string): tails' file location (URL)
     - `issuanceType` (string enum): defines credentials revocation strategy. Can have the following values:
        - `ISSUANCE_BY_DEFAULT`: all credentials are assumed to be issued initially, so that Revocation Registry needs to be updated (REVOC_REG_ENTRY txn sent) only when revoking. Revocation Registry stores only revoked credentials indices in this case. Recommended to use if expected number of revocation actions is less than expected number of issuance actions. 
        - `ISSUANCE_ON_DEMAND`: no credentials are issued initially, so that Revocation Registry needs to be updated (REVOC_REG_ENTRY txn sent) on every issuance and revocation. Revocation Registry stores only issued credentials indices in this case. Recommended to use if expected number of issuance actions is less than expected number of revocation actions.
     - `publicKeys` (dict): Revocation Registry's public key

- `id` (string): Revocation Registry Definition's unique identifier (a key from state trie is currently used)
- `credDefId` (string): The corresponding Credential Definition's unique identifier (a key from state trie is currently used)
- `revocDefType` (string enum): Revocation Type. `CL_ACCUM` (Camenisch-Lysyanskaya Accumulator) is the only supported type now.
- `tag` (string): A unique tag to have multiple Revocation Registry Definitions for the same Credential Definition and type issued by the same DID. 

*Request Example*:
```
{
    'operation': {
        'type': '113',
        'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'credDefId': 'FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag'
        'revocDefType': 'CL_ACCUM',
        'tag': 'tag1',
        'value': {
            'maxCredNum': 1000000,
            'tailsHash': '6619ad3cf7e02fc29931a5cdc7bb70ba4b9283bda3badae297',
            'tailsLocation': 'http://tails.location.com',
            'issuanceType': 'ISSUANCE_BY_DEFAULT',
            'publicKeys': {},
        },
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'endorser': 'D6HG5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 2,
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
            "type":"113",
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
                'credDefId': 'FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag'
                'revocDefType': 'CL_ACCUM',
                'tag': 'tag1',
                'value': {
                    'maxCredNum': 1000000,
                    'tailsHash': '6619ad3cf7e02fc29931a5cdc7bb70ba4b9283bda3badae297',
                    'tailsLocation': 'http://tails.location.com',
                    'issuanceType': 'ISSUANCE_BY_DEFAULT',
                    'publicKeys': {},
                },
            },
            
            "metadata": {
                "reqId":1514280215504647,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
                "endorser": "D6HG5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS"
            }]
        },
        
        'rootHash': '5vasvo2NUAD7Gq8RVxJZg1s9F7cBpuem1VgHKaFP8oBm',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '66BCs5tG7qnfK6egnDsvcx2VSNH6z1Mfo9WmhLSExS6b'],
        
    }
}
```

### REVOC_REG_ENTRY
The RevocReg entry containing the new accumulator value and issued/revoked indices. This is just a delta of indices, not the whole list. So, it can be sent each time a new claim is issued/revoked.

- `value` (dict):

     Dictionary with revocation registry's data:
     
     - `accum` (string): the current accumulator value
     - `prevAccum` (string): the previous accumulator value; it's compared with the current value, and txn is rejected if they don't match; it's needed to avoid dirty writes and updates of accumulator.
     - `issued` (list of integers): an array of issued indices (may be absent/empty if the type is ISSUANCE_BY_DEFAULT); this is delta; will be accumulated in state.
     - `revoked` (list of integers):  an array of revoked indices (delta; will be accumulated in state)    

- `revocRegDefId` (string): The corresponding Revocation Registry Definition's unique identifier (a key from state trie is currently used)
- `revocDefType` (string enum): Revocation Type. `CL_ACCUM` (Camenisch-Lysyanskaya Accumulator) is the only supported type now.

*Request Example*:
```
{
    'operation': {
        'type': '114',
            'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1'
            'revocDefType': 'CL_ACCUM',
            'value': {
                'accum': 'accum_value',
                'prevAccum': 'prev_acuum_value',
                'issued': [],
                'revoked': [10, 36, 3478],
            },
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'endorser': 'D6HG5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 2,
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
            "type":"114",
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1'
                'revocDefType': 'CL_ACCUM',
                'value': {
                    'accum': 'accum_value',
                    'prevAccum': 'prev_acuum_value',
                    'issued': [],
                    'revoked': [10, 36, 3478],
                },
            },
            
            "metadata": {
                "reqId":1514280215504647,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
                "endorser": "D6HG5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
            },
        },
        "txnMetadata": {
            "txnTime":1513945121,
            "seqNo": 10,  
            "txnId":"5:L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1",
        },
        "reqSignature": {
            "type": "ED25519",
            "values": [{
                "from": "L5AD5g65TDQr1PPHHRoiGf",
                "value": "5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS"
            }]
        },
        
        'rootHash': '5vasvo2NUAD7Gq8RVxJZg1s9F7cBpuem1VgHKaFP8oBm',
        'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '66BCs5tG7qnfK6egnDsvcx2VSNH6z1Mfo9WmhLSExS6b'],
        
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

    Target Node's verkey as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the transaction submitter (Steward's DID).

    *Example*: `identifier` is a DID of a Steward creating a new Node, and `dest` is the verkey of this Node.

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
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
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
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
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
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
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
    'protocolVersion': 2,
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
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                "writes":false,
                "force":true,
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
    }
}
```

### AUTH_RULE

A command to change authentication rules. 
Internally authentication rules are stored as a key-value dictionary: `{action} -> {auth_constraint}`.

The list of actions is static and can be found in [auth_rules.md](auth_rules.md).
There is a default Auth Constraint for every action (defined in [auth_rules.md](auth_rules.md)). 

The `AUTH_RULE` command allows to change the Auth Constraint.
So, it's not possible to register new actions by this command. But it's possible to override authentication constraints (values) for the given action.

Please note, that list elements of `GET_AUTH_RULE` output can be used as an input (with a required changes) for `AUTH_RULE`.

If format of a transaction is incorrect, the client will receive NACK message for the request. 
A client will receive NACK for 
- a request with incorrect format;
- a request with "ADD" action, but with "old_value";
- a request with "EDIT" action without "old_value";
- a request with a key that is not in the [auth_rule](auth_rule.md).

The following input parameters must match an auth rule from the [auth_rules.md](auth_rules.md):
- `auth_type` (string enum)
 
     The type of transaction to change the auth constraints to. (Example: "0", "1", ...). See transactions description to find the txn type enum value.

- `auth_action` (enum: `ADD` or `EDIT`)

    Whether this is addign of a new transaction, or editting of an existing one.
    
- `field` (string)
 
    Set the auth constraint of editing the given specific field. `*` can be used to specify that an auth rule is applied to all fields.
    
- `old_value` (string; optional)

    Old value of a field, which can be changed to a new_value. Must be present for EDIT `auth_action` only.
    `*` can be used if it doesn't matter what was the old value.
    
- `new_value` (string)

    New value that can be used to fill the field.
    `*` can be used if it doesn't matter what was the old value.

The `constraint_id` fields is where one can define the desired auth constraint for the action:

- `constraint` (dict)

    - `constraint_id` (string enum)
    
        Constraint Type. As of now, the following constraint types are supported:
            
            - 'ROLE': a constraint defining how many signatures of a given role are required
            - 'OR': logical disjunction for all constraints from `auth_constraints` 
            - 'AND': logical conjunction for all constraints from `auth_constraints`
            - 'FORBIDDEN': a constraint for not allowed actions
            
    - fields if `'constraint_id': 'OR'` or `'constraint_id': 'AND'`
    
        - `auth_constraints` (list)
        
            A list of constraints. Any number of nested constraints is supported recursively
        
    - fields if `'constraint_id': 'ROLE'`:
                
        - `role` (string enum)    
            
            Who (what role) can perform the action
            Please have a look at [NYM](#nym) transaction description for a mapping between role codes and names.
                
        - `sig_count` (int):
        
            The number of signatures that is needed to do the action
            
        - `need_to_be_owner` (boolean):
        
            Flag to check if the user must be the owner of a transaction (Example: A steward must be the owner of the node to make changes to it).
            The notion of the `owner` is different for every auth rule. Please reference to [auth_rules.md](auth_rules.md) for details.
            
        - `off_ledger_signature` (boolean, optional, False by default):
        
            Whether signatures against keys not present on the ledger are accepted during verification of the required number of valid signatures.
            An example when it can be set to `True` is creation of a new DID in a permissionless mode, that is when `identifer` is not present on the ledger and a newly created `verkey` is used for signature verification.
            Another example is signing by cryptonyms  (where identifier is equal to verkey), but this is not supported yet. 
            If the value of this field is False (default), and the number of required signatures is greater than zero, then the transaction author's DID (`identifier`) must be present on the ledger (corresponding NYM txn must exist).            
            
        - `metadata` (dict; optional):
        
            Dictionary for additional parameters of the constraint. Can be used by plugins to add additional restrictions.
        
    - fields if `'constraint_id': 'FORBIDDEN'`:
    
        no fields


*Request Example*:

Let's consider an example of changing a value of a NODE transaction's `service` field from `[VALIDATOR]` to `[]` (demotion of a node).
 We are going to set an Auth Constraint, so that the action can be only be done by two TRUSTEE or one STEWARD who is the owner (the original creator) of this transaction.
 
```
{
    'operation': {
        'type':'120',
        'auth_type': '0', 
        'auth_action': 'EDIT',
        'field' :'services',
        'old_value': [VALIDATOR],
        'new_value': []
        'constraint':{
              'constraint_id': 'OR',
              'auth_constraints': [{'constraint_id': 'ROLE', 
                                    'role': '0',
                                    'sig_count': 2, 
                                    'need_to_be_owner': False, 
                                    'metadata': {}}, 
                                   
                                   {'constraint_id': 'ROLE', 
                                    'role': '2',
                                    'sig_count': 1, 
                                    'need_to_be_owner': True, 
                                    'metadata': {}}
                                   ]
        }, 
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 2,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj'
}
```

*Reply Example*:
```
{     'op':'REPLY',
      'result':{  
         'txnMetadata':{  
            'seqNo':1,
            'txnTime':1551776783
         },
         'reqSignature':{  
            'values':[  
               {  
                  'value':'4j99V2BNRX1dn2QhnR8L9C3W9XQt1W3ScD1pyYaqD1NUnDVhbFGS3cw8dHRe5uVk8W7DoFtHb81ekMs9t9e76Fg',
                  'from':'M9BJDuS24bqbJNvBRsoGg3'
               }
            ],
            'type':'ED25519'
         },
         'txn':{  
            'data':{  
                'auth_type': '0', 
                'auth_action': 'EDIT',
                'field' :'services',
                'old_value': [VALIDATOR],
                'new_value': []            
                'constraint':{  
                          'constraint_id': 'OR',
                          'auth_constraints': [{'constraint_id': 'ROLE', 
                                                'role': '0',
                                                'sig_count': 2, 
                                                'need_to_be_owner': False, 
                                                'metadata': {}}, 
                                               
                                               {'constraint_id': 'ROLE', 
                                                'role': '2',
                                                'sig_count': 1, 
                                                'need_to_be_owner': True, 
                                                'metadata': {}}
                                               ]
                }, 
            },
            'protocolVersion':2,
            'metadata':{  
               'from':'M9BJDuS24bqbJNvBRsoGg3',
               'digest':'ea13f0a310c7f4494d2828bccbc8ff0bd8b77d0c0bfb1ed9a84104bf55ad0436',
               'payloadDigest': '21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685',
               'reqId':711182024
            },
            'type':'120'
         },
         'ver':'1',
         'rootHash':'GJNfknLWDAb8R93cgAX3Bw6CYDo23HBhiwZnzb4fHtyi',
         'auditPath':['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6']
      }
   }
```


### AUTH_RULES

A command to set multiple AUTH_RULEs by one transaction. 
Transaction AUTH_RULES is not divided into a few AUTH_RULE transactions, and is written to the ledger with one transaction with the full set of rules that come in the request.
Internally authentication rules are stored as a key-value dictionary: `{action} -> {auth_constraint}`.

The list of actions is static and can be found in [auth_rules.md](auth_rules.md).
There is a default Auth Constraint for every action (defined in [auth_rules.md](auth_rules.md)). 

The `AUTH_RULES` command allows to change the Auth Constraints.
So, it's not possible to register new actions by this command. But it's possible to override authentication constraints (values) for the given action.

Please note, that list elements of `GET_AUTH_RULE` output can be used as an input (with a required changes) for the field `rules` in `AUTH_RULES`.

If one rule is incorrect, the client will receive NACK message for the request with all its rules.
A client will receive NACK for 
- a request with incorrect format;
- a request with a rule with "ADD" action, but with "old_value";
- a request with a rule with "EDIT" action without "old_value";
- a request with a rule with a key that is not in the [auth_rule](auth_rule.md).

- The `rules` field contains a list of auth rules. One rule has the following list of parameters which must match an auth rule from the [auth_rules.md](auth_rules.md):

  - `auth_type` (string enum)
 
     The type of transaction to change the auth constraints to. (Example: "0", "1", ...). See transactions description to find the txn type enum value.

  - `auth_action` (enum: `ADD` or `EDIT`)

    Whether this is adding of a new transaction, or editing of an existing one.
    
  - `field` (string)
 
    Set the auth constraint of editing the given specific field. `*` can be used to specify that an auth rule is applied to all fields.
    
  - `old_value` (string; optional)

    Old value of a field, which can be changed to a new_value. Must be present for EDIT `auth_action` only.
    `*` can be used if it doesn't matter what was the old value.
    
  - `new_value` (string)

    New value that can be used to fill the field.
    `*` can be used if it doesn't matter what was the old value.

  The `constraint_id` fields is where one can define the desired auth constraint for the action:

  - `constraint` (dict)

    - `constraint_id` (string enum)
    
        Constraint Type. As of now, the following constraint types are supported:
            
            - 'ROLE': a constraint defining how many signatures of a given role are required
            - 'OR': logical disjunction for all constraints from `auth_constraints` 
            - 'AND': logical conjunction for all constraints from `auth_constraints`
            - 'FORBIDDEN': a constraint for not allowed actions
            
    - fields if `'constraint_id': 'OR'` or `'constraint_id': 'AND'`
    
        - `auth_constraints` (list)
        
            A list of constraints. Any number of nested constraints is supported recursively
        
    - fields if `'constraint_id': 'ROLE'`:
                
        - `role` (string enum)    
            
            Who (what role) can perform the action
            Please have a look at [NYM](#nym) transaction description for a mapping between role codes and names.
                
        - `sig_count` (int):
        
            The number of signatures that is needed to do the action
            
        - `need_to_be_owner` (boolean):
        
            Flag to check if the user must be the owner of a transaction (Example: A steward must be the owner of the node to make changes to it).
            The notion of the `owner` is different for every auth rule. Please reference to [auth_rules.md](auth_rules.md) for details.
            
        - `off_ledger_signature` (boolean, optional, False by default):
        
            Whether signatures against keys not present on the ledger are accepted during verification of required number of valid signatures.
            An example when it can be set to `True` is creation of a new DID in a permissionless mode, that is when `identifer` is not present on the ledger and a newly created `verkey` is used for signature verification.
            Another example is signing by cryptonyms  (where identifier is equal to verkey), but this is not supported yet. 
            If the value of this field is False (default), and the number of required signatures is greater than zero, then the transaction author's DID (`identifier`) must be present on the ledger (corresponding NYM txn must exist).
            
        - `metadata` (dict; optional):
        
            Dictionary for additional parameters of the constraint. Can be used by plugins to add additional restrictions.
        
    - fields if `'constraint_id': 'FORBIDDEN'`:
    
        no fields

*Request Example*:
```
{
    'operation': {
           'type':'122',
           'rules': [
                {'constraint':{  
                     'constraint_id': 'OR',
                     'auth_constraints': [{'constraint_id': 'ROLE', 
                                           'role': '0',
                                           'sig_count': 1, 
                                           'need_to_be_owner': False, 
                                           'metadata': {}}, 
                                                               
                                           {'constraint_id': 'ROLE', 
                                            'role': '2',
                                            'sig_count': 1, 
                                            'need_to_be_owner': True, 
                                            'metadata': {}}
                                           ]
                   }, 
                 'field' :'services',
                 'auth_type': '0', 
                 'auth_action': 'EDIT',
                 'old_value': [VALIDATOR],
                 'new_value': []
                },
                ...
           ]
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 1,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj'
}
```

*Reply Example*:
```
{     'op':'REPLY',
      'result':{  
         'txnMetadata':{  
            'seqNo':1,
            'txnTime':1551776783
         },
         'reqSignature':{  
            'values':[  
               {  
                  'value':'4j99V2BNRX1dn2QhnR8L9C3W9XQt1W3ScD1pyYaqD1NUnDVhbFGS3cw8dHRe5uVk8W7DoFtHb81ekMs9t9e76Fg',
                  'from':'M9BJDuS24bqbJNvBRsoGg3'
               }
            ],
            'type':'ED25519'
         },
         'txn':{  
            'type':'122',
            'data':{
               'rules': [
                    {'constraint':{  
                         'constraint_id': 'OR',
                         'auth_constraints': [{'constraint_id': 'ROLE', 
                                               'role': '0',
                                               'sig_count': 1, 
                                               'need_to_be_owner': False, 
                                               'metadata': {}}, 
                                                                   
                                               {'constraint_id': 'ROLE', 
                                                'role': '2',
                                                'sig_count': 1, 
                                                'need_to_be_owner': True, 
                                                'metadata': {}}
                                               ]
                       }, 
                     'field' :'services',
                     'auth_type': '0', 
                     'auth_action': 'EDIT',
                     'old_value': [VALIDATOR],
                     'new_value': []
                    },
                    ...
               ]
            }
            'protocolVersion':2,
            'metadata':{  
               'from':'M9BJDuS24bqbJNvBRsoGg3',
               'digest':'ea13f0a310c7f4494d2828bccbc8ff0bd8b77d0c0bfb1ed9a84104bf55ad0436',
               'reqId':711182024
            }
         },
         'ver':'1',
         'rootHash':'GJNfknLWDAb8R93cgAX3Bw6CYDo23HBhiwZnzb4fHtyi',
         'auditPath':[  

         ]
      }
   }
```


### TRANSACTION_AUTHOR_AGREEMENT

Setting (enabling/disabling) a transaction author agreement for the pool.

If transaction author agreement is set, then all write requests to Domain ledger (transactions) must include additional metadata pointing to the latest transaction author agreement's digest which is signed by the transaction author.
If no transaction author agreement is set, or there are no active transaction author agreements, then no additional metadata is required.

Each transaction author agreement has a unique version.
If TRANSACTION_AUTHOR_AGREEMENT transaction is sent for already existing version it is considered an update 
(for example of retirement timestamp), in this case text and ratification timestamp should be either absent or equal to original values.

For any given version of transaction author agreement text and ratification timestamp cannot be changed once set. Ratification timestamp cannot be in future.
In order to update Transaction Author Agreement `TRANSACTION_AUTHOR_AGREEMENT` transaction should be sent, 
containing new version and new text of agreement. This makes it possible to use new Transaction Author Agreement, but doesn't disable previous one automatically.

Individual transaction author agreements can be disabled by setting retirement timestamp using same transaction.
Retirement timestamp can be in future, in this case deactivation of agreement won't happen immediately, it will be automatically deactivated at required time instead.

It is possible to change existing retirement timestamp of agreement by sending a `TRANSACTION_AUTHOR_AGREEMENT` transaction with a new retirement timestamp.
This may potentially re-enable already retired Agreement.
Re-enabling retired Agreement needs to be considered as an exceptional case used mostly for fixing disabling by mistake or with incorrect retirement timestamp specified.
 
It is possible to delete retirement timestamp of agreement by sending a `TRANSACTION_AUTHOR_AGREEMENT` transaction without a retirement timestamp or retirement timestamp set to `None`.
This will either cancel retirement (if it hasn't occurred yet), or disable retirement of already retired transaction (re-enable the Agreement).
Re-enabling retired Agreement needs to be considered as an exceptional case used mostly for fixing disabling by mistake or with incorrect retirement timestamp specified.

Latest transaction author agreement cannot be disabled using this transaction.
 
It is possible to disable all currently active transaction author agreements (including latest) using separate transaction [TRANSACTION_AUTHOR_AGREEMENT_DISABLE](#transaction_author_agreement_disable).
This will immediately set current timestamp as retirement one for all not yet retired Transaction Author Agreements.

It's not possible to re-enable an Agreement right after disabling all agreements because there is no active latest Agreement at this point.
A new Agreement needs to be sent instead.

At least one [TRANSACTION_AUTHOR_AGREEMENT_AML](#transaction_author_agreement_aml) must be set on the ledger before submitting TRANSACTION_AUTHOR_AGREEMENT txn.

- `version` (string):

    Unique version of the transaction author agreement

- `text` (string; optional):

    Transaction author agreement's text. Must be specified when creating a new Agreement.
    Should be either omitted or equal to existing value in case of updating an existing Agreement (setting `retirement_ts`) .

- `ratification_ts` (integer as POSIX timestamp; optional):

    Timestamp of Transaction Author Agreement ratification date as POSIX timestamp. May have any precision up to seconds.
    Must be specified when creating a new Agreement.
    Should be either omitted or equal to existing value in case of updating an existing Agreement (setting `retirement_ts`).

- `retirement_ts` (integer as POSIX timestamp; optional):

    Timestamp of Transaction Author Agreement retirement date as POSIX timestamp. May have any precision up to seconds.
    Can be any timestamp either in future or in the past (the Agreement will be retired immediately in the latter case).
    Must be omitted when creating a new (latest) Agreement.
    Should be used for updating (deactivating) non-latest Agreement on the ledger.
    
*New Agreement Request Example*:
```
{
    'operation': {
        'type': '4'
        'version': '1.0',
        'text': 'Please read carefully before writing anything to the ledger',
        'ratification_ts': 1514304094738044
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 2,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj',
}
```

*New Agreement Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver":1,
        "txn": {
            "type":4,
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                'version': '1.0',
                'text': 'Please read carefully before writing anything to the ledger',
                'ratification_ts': 1514304094738044
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
    }
}
```


*Retire Agreement Request Example*:
```
{
    'operation': {
        'type': '4'
        'version': '1.0',
        'retirement_ts': 1515415195838044
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738066,
    'protocolVersion': 2,
    'signature': '3YVzDtSxxnowVwAXZmxCG2fz1A38j1qLrwKmGEG653GZw7KJRBX57Stc1oxQZqqu9mCqFLa7aBzt4MKXk4MeunVj',
}
```

*Retire Agreement Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        "ver":1,
        "txn": {
            "type":4,
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                'version': '1.0',
                'retirement_ts': 1515415195838044
            },
            
            "metadata": {
                "reqId":1514304094738066,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
    }
}
```

### TRANSACTION_AUTHOR_AGREEMENT_AML

Setting a list of acceptance mechanisms for transaction author agreement.

Each write request for which a transaction author agreement needs to be accepted must point to a  mechanism from the latest list on the ledger. The chosen mechanism is signed by the write request author (together with the transaction author agreement digest). 


Each acceptance mechanisms list has a unique version.

- `version` (string):

    Unique version of the transaction author agreement acceptance mechanisms list


- `aml` (dict):

    Acceptance mechanisms list data in the form `<acceptance mechanism label>: <acceptance mechanism description>`
    
- `amlContext` (string, optional):

    A context information about Acceptance mechanisms list (may be URL to external resource).   

*Request Example*:
```
{
    'operation': {
        'type': '5'
        "version": "1.0",
        "aml": {
            "EULA": "Included in the EULA for the product being used",
            "Service Agreement": "Included in the agreement with the service provider managing the transaction",
            "Click Agreement": "Agreed through the UI at the time of submission",
            "Session Agreement": "Agreed at wallet instantiation or login"
        },
        "amlContext": "http://aml-context-descr"
    },
    
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 2,
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
            "type":5,
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                "version": "1.0",
                "aml": {
                    "EULA": "Included in the EULA for the product being used",
                    "Service Agreement": "Included in the agreement with the service provider managing the transaction",
                    "Click Agreement": "Agreed through the UI at the time of submission",
                    "Session Agreement": "Agreed at wallet instantiation or login"
                },
                "amlContext": "http://aml-context-descr"
            },
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
    }
}
```

### TRANSACTION_AUTHOR_AGREEMENT_DISABLE
Immediately retires all active Transaction Author Agreements at once by setting current timestamp as a retirement one.

It's not possible to re-enable an Agreement right after disabling all agreements because there is no active latest Agreement at this point.
A new Agreement needs to be sent instead.

*Request Example*:
```
{
    'operation': {
        'type': '8'
    },
    'identifier': '21BPzYYrFzbuECcBV3M1FH',
    'reqId': 1514304094738044,
    'protocolVersion': 2,
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
            "type":8,
            "protocolVersion":2,
            
            "data": {},
            
            "metadata": {
                "reqId":1514304094738044,
                "from":"21BPzYYrFzbuECcBV3M1FH",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
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
        },
        
        'rootHash': 'DvpkQ2aADvQawmrzvTTjF9eKQxjDkrCbQDszMRbgJ6zV',
        'auditPath': ['6GdvJfqTekMvzwi9wuEpfqMLzuN1T91kvgRBQLUzjkt6'],
    }
}
```

### SET_CONTEXT
Adds Context.

It's not possible to update existing Context.
So, if the Context needs to be evolved, a new Context with a new version or name needs to be created.

- `data` (dict):

     Dictionary with Context's data:
     
    - `@context`: This value must be either:
        1) a URI (it should dereference to a Context object)
        2) a Context object (a dict)
        3) an array of Context objects and/or Context URIs

- `meta` (dict)

    Dictionary with Context's metadata
    
    - `name`: Context's name string
    - `version`: Context's version string
    - `type`: 'ctx'

*Request Example*:
```
{
    'operation': {
        'type': '200',
        "data":{
            "@context": [
                {
                    "@version": 1.1
                },
                "https://www.w3.org/ns/odrl.jsonld",
                {
                    "ex": "https://example.org/examples#",
                    "schema": "http://schema.org/",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                }
            ]
        },
        "meta": {
            "name":"SimpleContext",
            "version":"1.0",
            "type": "ctx"
        },
    },
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'endorser': 'D6HG5g65TDQr1PPHHRoiGf',
    'reqId': 1514280215504647,
    'protocolVersion': 2,
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
            "type":"200",
            "protocolVersion":2,
            
            "data": {
                "ver":1,
                "data":{
                    "@context": [
                        {
                            "@version": 1.1
                        },
                        "https://www.w3.org/ns/odrl.jsonld",
                        {
                            "ex": "https://example.org/examples#",
                            "schema": "http://schema.org/",
                            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                        }
                    ]
                },
                "meta": {
                    "name":"SimpleContext",
                    "version":"1.0",
                    "type": "ctx"
                },
            },
            
            "metadata": {
                "reqId":1514280215504647,
                "from":"L5AD5g65TDQr1PPHHRoiGf",
                "endorser": "D6HG5g65TDQr1PPHHRoiGf",
                "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
                "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685"
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
    'protocolVersion': 2
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
    'protocolVersion': 2
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
    'protocolVersion': 2
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
    'protocolVersion': 2
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

### GET_REVOC_REG_DEF

Gets a Revocation Registry Definition, that Issuer creates and publishes for a particular Claim Definition.

- `id` (string): Revocation Registry Definition's unique identifier (a key from state trie is currently used)

*Request Example*:
```
{
    'operation': {
        'type': '115'
        'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
    },
    
    'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '115',
        'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        
        'seqNo': 10,
        'txnTime': 1514214795,
        
        'data': {
            'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
            'credDefId': 'FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag'
            'revocDefType': 'CL_ACCUM',
            'tag': 'tag1',
            'value': {
                'maxCredNum': 1000000,
                'tailsHash': '6619ad3cf7e02fc29931a5cdc7bb70ba4b9283bda3badae297',
                'tailsLocation': 'http://tails.location.com',
                'issuanceType': 'ISSUANCE_BY_DEFAULT',
                'publicKeys': {},
            },
        },
        

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
        

    }
}
```

### GET_REVOC_REG

Gets a Revocation Registry Accumulator.

- `revocRegDefId` (string): The corresponding Revocation Registry Definition's unique identifier (a key from state trie is currently used)

- `timestamp` (integer as POSIX timestamp):

    The time (from the ledger point of view) for which we want to get the accumulator value.

*Request Example*:
```
{
    'operation': {
        'type': '116'
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'timestamp': 1514214800
    },
    
    'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '116',
        'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'timestamp': 1514214800
        
        'seqNo': 10,
        'txnTime': 1514214795,
        
        'data': {
            'id': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
            'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1'
            'revocDefType': 'CL_ACCUM',
            'value': {
                'accum': 'accum_value',
            },
        },
        

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
        

    }
}
```

### GET_REVOC_REG_DELTA

Gets a Revocation Registry Delta (accum values, and delta of issues/revoked indices) for the given time interval (`from` and `to`).

If from is not set, then the whole registry (accum and current issues/revoked indices) is returned for the given time (`to`)

- `revocRegDefId` (string): The corresponding Revocation Registry Definition's unique identifier (a key from state trie is currently used)

- `from` (integer as POSIX timestamp, optional):

    The time (from the ledger point of view) we want to return accum and indices after, that is the left bound of the delta interval. Can be absent, which means that all indices and accum needs to be returned till `to`.

- `to` (integer as POSIX timestamp):

    The time (from the ledger point of view) we want to return accum and indices before, that is the right bound of the delta interval. 


Please note, that if `from` is set, then addition state proof for `accum_from` value is returned in `stateProofFrom`, while the common state proof is for `accum_to`
Both state proofs are returned just for accumulator values. The client needs to check that the returned delta is also correct by calculating `accum_to` from the given `accum_from` and delta indices, and making sure that the calculated  `accum_to` is equal to the returned one.

If `from` is not set, then there is just one state proof (as usual) for both `accum` value and the whole indices lists. 

*Request Example when both `from` and `to` present*:
```
{
    'operation': {
        'type': '117'
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'from': 1514214100
        'to': 1514214900
    },
    
    'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example when both `from` and `to` present*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '117',
        'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'from': 1514214100
        'to': 1514214900
        
        'seqNo': 18,
        'txnTime': 1514214795,
        
        'data': {
            'revocDefType': 'CL_ACCUM',
            'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
            'value': {
               'accum_to': {
                   'revocDefType': 'CL_ACCUM', 
                   'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1', 
                   'txnTime': 1514214795, 
                   'seqNo': 18,
                   'value': {
                      'accum': '9a512a7624'
                   }
                },
                'revoked': [10, 11],
                'issued': [1, 2, 3], 
                'accum_from': {
                    'revocDefType': 'CL_ACCUM',
                    'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1', 
                    'txnTime': 1514214105, 
                    'seqNo': 16, 
                    'value': {
                       'accum': 'be080bd74b'
                    }
                 }
            },
            'stateProofFrom': {
                'multi_signature': {
                     'participants': ['Delta', 'Gamma', 'Alpha'],
                     'signature': 'QpP4oVm2MLQ7SzLVZknuFjneXfqYj6UStn3oQtCdSiKiYuS4n1kxRphKRDMwmS7LGeXgUmy3C8GtcVM5X9SN9qLr2MBApjpPtKE9DkBTwyieh3vN1UMq1Kwx2Jkz7vcSJNH2WzjEKSUnpFLEJk4mpFaibqd1xX2hrwruxzSDUi2uCT', 
                     'value': {
                         'state_root_hash': '2sfnQcEKkjw78KYnGJyk5Gw9gtwESvX6NdFFPEiQYQsz', 
                         'ledger_id': 1,
                         'pool_state_root_hash': 'JDt3NNrZenx3x41oxsvhWeuSFFerdyqEvQUWyGdHX7gx',
                         'timestamp': 1514214105, 
                         'txn_root_hash': 'FCkntnPqfaGx4fCX5tTdWeLr1mXdFuZnTNuEehiet32z'
                     }
                },
                'root_hash': '2sfnQcEKkjw78KYnGJyk5Gw9gtwESvX6NdFFPEiQYQsz',
                'proof_nodes': '+QLB+QE3uFEgOk1TaktUV2tQTHRZb1BFYVRGMVRVRGI6NDpNU2pLVFdrUEx0WW9QRWFURjFUVURiOjM6Q0w6MTM6c29tZV90YWc6Q0xfQUNDVU06YTk4ZWO44vjguN57ImxzbiI6MTYsImx1dCI6MTU1ODUyNDEzMSwidmFsIjp7InJldm9jRGVmVHlwZSI6IkNMX0FDQ1VNIiwicmV2b2NSZWdEZWZJZCI6Ik1TaktUV2tQTHRZb1BFYVRGMVRVRGI6NDpNU2pLVFdrUEx0WW9QRWFURjFUVURiOjM6Q0w6MTM6c29tZV90YWc6Q0xfQUNDVU06YTk4ZWMiLCJzZXFObyI6MTYsInR4blRpbWUiOjE1NTg1MjQxMzEsInZhbHVlIjp7ImFjY3VtIjoiYmUwODBiZDc0YiJ9fX34UYCAgICAoAgDh8v1CXNEJGFl302RO98x8R6Ozscy0ZFdRpiCobh3oCnaxHyPnZq6E+mbnfU6oC994Wv1nh7sf0pQOp5g93tbgICAgICAgICAgPkBMYCAgKBmZE7e2jSrhTw9usjxZcAb25uSisJV+TzkbXNUypyJvaA/KAFG4RQqB9dAGRfTgly2XjXvPCeVr7vBn6FSkN7sH4CAoBGxQDip9XfEC/CkgimSkkhCeMm9XnkxxwWiMJwzuhAjgKAmh0g8FUI60e7NBwTu7ukdfz6kaON6u9U87kTeTlPcXICgsk2X2G6MlVhEqMEzthWAT4ey6qRaKXpOuMZOA1kMODagQdHobiexMaAwqtI7P5bbfqNkQEoZD79m6z43DEGQGL6gXQfLXgd+xWWXypr1pDxPvjSU8UtHjfWhJ58aiuqAzmKgyee3YL7GFFd+5oxG9b/q4od/mRjFpLdXKR3YG2o/hAygRIVVdoVD0dpqktsN8kSc03UhYiI76nxdCejX+CV4OX6A'
            }
        },
        

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
        

    }
}
```



*Request Example when there is only `to` present*:
```
{
    'operation': {
        'type': '117'
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'to': 1514214900
    },
    
    'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example when there is only `to` present*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '117',
        'identifier': 'T6AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
        'to': 1514214900
        
        'seqNo': 18,
        'txnTime': 1514214795,
        
        'data': {
            'revocDefType': 'CL_ACCUM',
            'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1',
            'value': {
               'accum_to': {
                   'revocDefType': 'CL_ACCUM', 
                   'revocRegDefId': 'L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1', 
                   'txnTime': 1514214795, 
                   'seqNo': 18,
                   'value': {
                      'accum': '9a512a7624'
                   }
                },
                'issued': [],
                'revoked': [1, 2, 3, 4, 5]
        },
        

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
        

    }
}
```

### GET_AUTH_RULE

A request to get an auth constraint for an authentication rule or a full list of rules from Ledger. The constraint format is described in [AUTH_RULE transaction](#auth_rule).

The set of Auth Rules is static and can be found in [auth_rules.md](auth_rules.md). This is the constraint part that may be changed and edited. 

Two options are possible in a request builder:
- If the request has a full list of parameters (probably without `old_value` as it's not required for ADD actions), then the reply will contain one constraint for this key.
- If the request does not contain fields other than txn_type, the response will contain a full list of authentication rules.

A reply is a list of Auth Rules with constraints. This will be a one-element list in case of GET_AUTH_RULE with params, that is GET_AUTH_RULE for specific action.

Each output list element is equal to the input of [AUTH_RULE](#auth_rule), so list elements of `GET_AUTH_RULE` output can be used as an input (with a required changes) for `AUTH_RULE`.


- `auth_action` (enum: `ADD` or `EDIT`; optional):

    Action type: add a new entity or edit an existing one.
    
- `auth_type` (string; optional):

    The type of transaction to change rights for. (Example: "0", "1", ...)

- `field` (string; optional):

    Change the rights for editing (adding) a value of the given transaction field. `*` can be used as `any field`.

- `old_value` (string; optional):

   Old value of a field, which can be changed to a new_value. Makes sense for EDIT actions only.

- `new_value` (string; optional):
   
   New value that can be used to fill the field.

*Request Example (for getting one rule)*:
```
  {  
      'reqId':572495653,
      'signature':'366f89ehxLuxPySGcHppxbURWRcmXVdkHeHrjtPKNYSRKnvaxzUXF8CEUWy9KU251u5bmnRL3TKvQiZgjwouTJYH',
      'identifier':'M9BJDuS24bqbJNvBRsoGg3',
      'operation':{  
            'auth_type': '0', 
            'auth_action': 'EDIT',
            'field' :'services',
            'old_value': [VALIDATOR],
            'new_value': []
      },
      'protocolVersion':2
   }
```

*Reply Example (for getting one rule)*:
```
{  
      'op':'REPLY',
      'result':{  
         'type':'121',
         'auth_type': '0', 
         'auth_action': 'EDIT',
         'field' :'services',
         'old_value': [VALIDATOR],
         'new_value': []
         
         'reqId':441933878,
         'identifier':'M9BJDuS24bqbJNvBRsoGg3',
         
         'data':[  
              {
                'auth_type': '0', 
                'auth_action': 'EDIT',
                'field' :'services',
                'old_value': [VALIDATOR],
                'new_value': []
                'constraint':{
                      'constraint_id': 'OR',
                      'auth_constraints': [{'constraint_id': 'ROLE', 
                                            'role': '0',
                                            'sig_count': 2, 
                                            'need_to_be_owner': False, 
                                            'metadata': {}}, 
                                           
                                           {'constraint_id': 'ROLE', 
                                            'role': '2',
                                            'sig_count': 1, 
                                            'need_to_be_owner': True, 
                                            'metadata': {}}
                                           ]
                }, 
              }
         ],

         'state_proof':{  
            'proof_nodes':'+Pz4+pUgQURELS0xLS1yb2xlLS0qLS0xMDG44vjguN57ImF1dGhfY29uc3RyYWludHMiOlt7ImNvbnN0cmFpbnRfaWQiOiJST0xFIiwibWV0YWRhdGEiOnt9LCJuZWVkX3RvX2JlX293bmVyIjpmYWxzZSwicm9sZSI6IjAiLCJzaWdfY291bnQiOjF9LHsiY29uc3RyYWludF9pZCI6IlJPTEUiLCJtZXRhZGF0YSI6e30sIm5lZWRfdG9fYmVfb3duZXIiOmZhbHNlLCJyb2xlIjoiMiIsInNpZ19jb3VudCI6MX1dLCJjb25zdHJhaW50X2lkIjoiQU5EIn0=',
            'root_hash':'DauPq3KR6QFnkaAgcfgoMvvWR6UTdHKZgzbjepqWaBqF',
            'multi_signature':{  
               'signature':'RNsPhUuPwwtA7NEf4VySCg1Fb2NpwapXrY8d64TLsRHR9rQ5ecGhRd89NTHabh8qEQ8Fs1XWawHjbSZ95RUYsJwx8PEXQcFEDGN3jc5VY31Q5rGg3aeBdFFxgYo11cZjrk6H7Md7N8fjHrKRdxo6TzDKSszJTNM1EAPLzyC6kKCnF9',
               'value':{  
                  'state_root_hash':'DauPq3KR6QFnkaAgcfgoMvvWR6UTdHKZgzbjepqWaBqF',
                  'pool_state_root_hash':'9L5CbxzhsNrZeGSJGVVpsC56JpuS5DGdUqfsFsR1RsFQ',
                  'timestamp':1552395470,
                  'txn_root_hash':'4CowHvnk2Axy2HWcYmT8b88A1Sgk45x7yHAzNnxowN9h',
                  'ledger_id':2
               },
               'participants':[  
                  'Beta',
                  'Gamma',
                  'Delta'
               ]
            }
         },
      }
}
```

*Request Example (for getting all rules)*:
```
  {  
      'reqId':575407732,
      'signature':'4AheMmtrfoHuAEtg5VsFPGe1j2w1UYxAvShRmfsCTSHnBDoA5EbmCa2xZzZVQjQGUFbYr65uznu1iUQhW22RNb1X',
      'identifier':'M9BJDuS24bqbJNvBRsoGg3',
      'operation':{  
         'type':'121'
      },
      'protocolVersion':2
  }
```

*Reply Example (for getting all rules)*:
```
{  
      'op':'REPLY',
      'result':{
         'type':'121',
           
         'reqId':575407732,
         'identifier':'M9BJDuS24bqbJNvBRsoGg3'

         'data':[  
              {
                'auth_type': '0', 
                'auth_action': 'EDIT',
                'field' :'services',
                'old_value': [VALIDATOR],
                'new_value': []
                'constraint':{
                      'constraint_id': 'OR',
                      'auth_constraints': [{'constraint_id': 'ROLE', 
                                            'role': '0',
                                            'sig_count': 2, 
                                            'need_to_be_owner': False, 
                                            'metadata': {}}, 
                                           
                                           {'constraint_id': 'ROLE', 
                                            'role': '2',
                                            'sig_count': 1, 
                                            'need_to_be_owner': True, 
                                            'metadata': {}}
                                           ]
                }, 
              },
              {
                'auth_type': '102', 
                'auth_action': 'ADD',
                'field' :'*',
                'new_value': '*'
                'constraint':{
                    'constraint_id': 'ROLE', 
                    'role': '2',
                    'sig_count': 1, 
                    'need_to_be_owner': False, 
                    'metadata': {}
                }, 
              },
              ........
         ],

      }
   }
```

### GET_TRANSACTION_AUTHOR_AGREEMENT

Gets a transaction author agreement.

- Gets the latest (current) transaction author agreement if no input parameter is set.
- Gets a transaction author agreement by its digest if `digest` is set. The digest is calculated from concatenation of [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)'s `version` and `text`.
- Gets a transaction author agreement by its version if `version` is set.
- Gets the latest (current) transaction author agreement at the given time (from ledger point of view) if `timestamp` is set.

The result contains Agreement's version, text, digest, ratification timestamp and retirement timestamp if it's set.

All input parameters are optional and mutually exclusive. 

- `digest` (sha256 digest hex string):

    Transaction's author agreement sha256 hash digest hex string calculated from concatenation of [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)'s `version` and `text`.
    
- `version` (string):

    Unique version of the transaction author agreement.
    
- `timestamp` (integer as POSIX timestamp):

    The time when transaction author agreement has been ordered (written to the ledger).


*Request Example*:
```
{
    'operation': {
        'type': '6'
        'version': '1.0',
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '6',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'version': '1.0',
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'data': {
            "version": "1.0",
            "text": "Please read carefully before writing anything to the ledger",
            "digest": "ca11c39b44ce4ec8666a8f63efd5bacf98a8e26c4f8890c87f629f126a3b74f3"
            "ratification_ts": 1514304094738044,
            "retirement_ts": 1515415195838044
        },

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 2, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
       
    }
}
```

### GET_TRANSACTION_AUTHOR_AGREEMENT_AML

Gets a transaction author agreement acceptance mechanisms list.

- Gets the latest (current) transaction author agreement acceptance mechanisms list if no input parameter is set.
- Gets a transaction author agreement acceptance mechanisms list by its version if `version` is set.
- Gets the latest (current) transaction author agreement acceptance mechanisms list at the given time (from ledger point of view) if `timestamp` is set.

All input parameters are optional and mutually exclusive. 

   
- `version` (string):

    Unique version of the transaction author agreement acceptance mechanisms list
    
- `timestamp` (integer as POSIX timestamp):

    The time when transaction author agreement acceptance mechanisms list has been ordered (written to the ledger).


*Request Example*:
```
{
    'operation': {
        'type': '7'
        'version': '1.0',
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '7',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514308188474704,
        
        'version': '1.0',
        
        'seqNo': 10,
        'txnTime': 1514214795,

        'data': {
            "version": "1.0",
            "aml": {
                "EULA": "Included in the EULA for the product being used",
                "Service Agreement": "Included in the agreement with the service provider managing the transaction",
                "Click Agreement": "Agreed through the UI at the time of submission",
                "Session Agreement": "Agreed at wallet instantiation or login"
            },
            "amlContext": "http://aml-context-descr"
        },

        'state_proof': {
            'root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH',
            'proof_nodes': '+QHl+FGAgICg0he/hjc9t/tPFzmCrb2T+nHnN0cRwqPKqZEc3pw2iCaAoAsA80p3oFwfl4dDaKkNI8z8weRsSaS9Y8n3HoardRzxgICAgICAgICAgID4naAgwxDOAEoIq+wUHr5h9jjSAIPDjS7SEG1NvWJbToxVQbh6+Hi4dnsiaWRlbnRpZmllciI6Ikw1QUQ1ZzY1VERRcjFQUEhIUm9pR2YiLCJyb2xlIjpudWxsLCJzZXFObyI6MTAsInR4blRpbWUiOjE1MTQyMTQ3OTUsInZlcmtleSI6In42dWV3Um03MmRXN1pUWFdObUFkUjFtIn348YCAgKDKj6ZIi+Ob9HXBy/CULIerYmmnnK2A6hN1u4ofU2eihKBna5MOCHiaObMfghjsZ8KBSbC6EpTFruD02fuGKlF1q4CAgICgBk8Cpc14mIr78WguSeT7+/rLT8qykKxzI4IO5ZMQwSmAoLsEwI+BkQFBiPsN8F610IjAg3+MVMbBjzugJKDo4NhYoFJ0ln1wq3FTWO0iw1zoUcO3FPjSh5ytvf1jvSxxcmJxoF0Hy14HfsVll8qa9aQ8T740lPFLR431oSefGorqgM5ioK1TJOr6JuvtBNByVMRv+rjhklCp6nkleiyLIq8vZYRcgIA=', 
            'multi_signature': {
                'value': {
                    'timestamp': 1514308168,
                    'ledger_id': 2, 
                    'txn_root_hash': '4Y2DpBPSsgwd5CVE8Z2zZZKS4M6n9AbisT3jYvCYyC2y',
                    'pool_state_root_hash': '9fzzkqU25JbgxycNYwUqKmM3LT8KsvUFkSSowD4pHpoK',
                    'state_root_hash': '81bGgr7FDSsf4ymdqaWzfnN86TETmkUKH4dj4AqnokrH'
                },
                'signature': 'REbtR8NvQy3dDRZLoTtzjHNx9ar65ttzk4jMqikwQiL1sPcHK4JAqrqVmhRLtw6Ed3iKuP4v8tgjA2BEvoyLTX6vB6vN4CqtFLqJaPJqMNZvr9tA5Lm6ZHBeEsH1QQLBYnWSAtXt658PotLUEp38sNxRh21t1zavbYcyV8AmxuVTg3',
                'participants': ['Delta', 'Gamma', 'Alpha']
            }
        },
        
       
    }
}
```

### GET_CONTEXT

Gets Context.

- `dest` (base58-encoded string):

    Context DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of the read request sender, and `dest` is the DID of the Context.

- `meta` (dict):

    - `name` (string):  Context's name string
    - `version` (string): Context's version string
    

 
*Request Example*:
```
{
    'operation': {
        'type': '300'
        'dest': '2VkbBskPNNyWrLrZq7DBhk',
        'meta': {
            'name': 'SimpleContext',
            'version': '1.0',
            'type': 'ctx'
        },
    },
    
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514308188474704,
    'protocolVersion': 2
}
```

*Reply Example*:
```
{
    'op': 'REPLY', 
    'result': {
        'type': '300',
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
        
        "data":{
            "@context": [
                {
                    "@version": 1.1
                },
                "https://www.w3.org/ns/odrl.jsonld",
                {
                    "ex": "https://example.org/examples#",
                    "schema": "http://schema.org/",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                }
            ]
        },

        "meta": {
            "name":"SimpleContext",
            "version":"1.0",
            "type": "ctx"
        },
        
        'dest': '2VkbBskPNNyWrLrZq7DBhk'
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
    'protocolVersion': 2
}
```

*Reply Example (returns requested NYM txn with seqNo=9)*:
```
{
    "op": "REPLY", 
    "result": {
        "type": "3",
        "identifier": "MSjKTWkPLtYoPEaTF1TUDb",
        "reqId": 1514311352551755,
       
        "seqNo": 9,

        "data": {
            "ver": 1,
            "txn": {
                "type":"1",
                "protocolVersion":2,
        
                "data": {
                    "ver": 1,
                    "dest":"GEzcdDLhCpGCYRHW82kjHd",
                    "verkey":"~HmUWn928bnFT6Ephf65YXv",
                    "role":101,
                },
        
                "metadata": {
                    "reqId":1513945121191691,
                    "from":"L5AD5g65TDQr1PPHHRoiGf",
                    "digest": "4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
                    "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
                    "taaAcceptance": {
                        "taaDigest": "6sh15d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
                        "mechanism": "EULA",
                        "time": 1513942017
                     }
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
                    "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
                }]
            }
        
            "rootHash": "5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn",
            "auditPath": ["Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA", "3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt"],
        }
        
        "type": "3",
        "reqId": 1514311281279625,
        "identifier": "MSjKTWkPLtYoPEaTF1TUDb",
        "seqNo": 9,
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
    'protocolVersion': 2,
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
