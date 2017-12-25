# Requests
This doc is about supported client's Request (both write and read ones).
If you are interested in transactions and their representation on the Ledger (that is internal one),
then have a look at [transactions](transactions.md).

[indy-sdk](https://github.com/hyperledger/indy-sdk) expects the format as specified below.

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

    The version of client-to-node protocol. Each new version may introduce a new feature in Requsts/Replies/Data.
    Since clients and different Nodes may be at different versions, we need this field to support backward compatibility
    between clients and nodes.     
    
- `signature` (base58-encoded string; mutually exclusive with `signatures` field):
 
    Submitter's signature.
    
- `signatures` (map of base58-encoded string; mutually exclusive with `signature` field): 
    
    Submitters' signature in multisig case. This is a map where cleint's identifiers are the keys and 
    base58-encoded signature strings are the values. 
    

Please find the format of each request-specific data for each type of request below.

## Common Reply Structure for Write Requests

Each Reply to write requests has a number of common metadata fields
(we don't support State Proofs for write requests yet). Most of these fields are actually metadata fields 
of a transaction in the Ledger (see [transactions](transactions.md)).

These common metadata values are added to result's JSON at the same level as real data.

**TODO**: consider distinguishing and separating real transaction data and metadata into different levels.
 

```
{
    'op': 'REPLY', 
    'result': {
        'type': '101',
        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514211108692476,
        'signature': '4pTTS4JeodhyQLxsYHr7iRXo9Q8kHL1pXnypZLUKzX5Rut5sFossZp7QSZiBueEYwYnkqpFaebzr94uHrHBu7ojS',
		'signatures': None,
		
		'seqNo': 10,
		'txnTime': 1514211268,
		
		'rootHash': '5ecipNPSztrk6X77fYPdepzFRUvLdqBuSqv4M9Mcv2Vn',
		'auditPath': ['Cdsoz17SVqPodKpe6xmY2ZgJ9UcywFDZTRgWSAYM96iA', '3phchUcMsnKFk2eZmcySAWm2T5rnzZdEypW7A5SKi1Qt'],
		
		<transaction-specific fields>
    }
}
```

- `type` (enum number as string): 

    Supported transaction types:
    
        - NODE = "0"
        - NYM = "1"
        - ATTRIB = "100"
        - SCHEMA = "101"
        - CLAIM_DEF = "102"
        - POOL_UPGRADE = "109"
        - NODE_UPGRADE = "110"
        - POOL_CONFIG = "111"

- `identifier` (base58-encoded string):
 
     as was in Request and saved as transaction's metadata on Ledger
     
- `reqId` (integer): 

    as was in Request and saved as transaction's metadata on Ledger
    
- `signature` (base58-encoded string; mutually exclusive with `signatures` field):
 
    as was in Request and saved as transaction's metadata on Ledger
    
- `signatures` (map of base58-encoded string; mutually exclusive with `signature` field): 
    
    as was in Request and saved as transaction's metadata on Ledger 
    
- `seqNo` (integer):

    a unique sequence number of the transaction on Ledger

- `txnTime` (integer as POSIX timestamp): 

    the time when transaction was written to the Ledger as POSIX timestamp
    
- `rootHash` (base58-encoded hash string):

    base58-encoded ledger's merkle tree root hash
    
- `auditPath` (array of base58-encoded hash strings):

    ledger's merkle tree audit proof as array of base58-encoded hash strings
    (this is a cryptographic proof to verify that the new transaction has 
    been appended to the ledger)
    
- transaction-specific fields as defined in [transactions](transactions.md) for each transaction type

## Reply Structure for Read Requests (except GET_TXN)

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

    as was in read (may differ from the `reqId` in `data` which defines 
    the request used to write the transaction to the Ledger)
    
- `seqNo` (integer):

    a unique sequence number of the transaction on Ledger

- `txnTime` (integer as POSIX timestamp): 

    the time when transaction was written to the Ledger as POSIX timestamp
    
      
## Write Requests

The format of each request-specific data for each type of request.
Please see [transactions](transactions.md) for detailed description of each field.

### NYM

- `dest` (base58-encoded string)
- `role` (enum number as string; optional) 
- `verkey` (base58-encoded string; optional) 
- `alias` (string; optional) 

*Request Example*:
```
{
    'operation': {
        'type': '1'
        'dest': 'N22KY2Dyvmuu2PyyqSFKue',
        'role': '101',
        'verkey': '31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE'
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
    'operation': {
        'type': '1'
        'dest': 'N22KY2Dyvmuu2PyyqSFKue',
        'role': '101',
        'verkey': '31V83xQnJDkZTSvm796X4MnzZFtUc96Tq6GJtuVkFQBE'
    },
    'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
    'reqId': 1514213797569745,
    'protocolVersion': 1,
    'signature': '49W5WP5jr7x1fZhtpAhHFbuUDqUYZ3AKht88gUjrz8TEJZr5MZUPjskpfBFdboLPZXKjbGjutoVascfKiMD5W7Ba',
}
```



### CLAIM_DEF

### SCHEMA

### NODE

### POOL_UPGRADE

### NODE_UPGRADE

### POOL_CONFIG




## Read Requests

