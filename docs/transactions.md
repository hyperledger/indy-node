# Transactions
This doc is about supported transactions and their representation on the Ledger (that is internal one).
If you are interested in the format of client's Request (both write and read ones), then have a look at [requests](requests.md).

- All transactions are stored in distributed Ledger (replicated on all Nodes) based on Merkle Tree. 
- The ledger consists of two things:
-- transactions log as a sequence of key-value pairs 
where key is a sequence number of the transaction and valur is serialized transaction
-- merkle tree (where hashes for leaves and nodes are persisted)
- Each transaction has a sequence number (no gaps) - keys in transactions log
- So, the it can be considered as a blockchain where each block size equals to 1
- There are multiple ledgers:
-- pool ledger: transactions related to pool/network configuration (listing all nodes, and their keys and addresses)
-- config ledger: transactions for pool configuration plus transactions related to Pool Upgrade
-- domain ledger: all main domain and application specific transactions (including NYM transactions for DID)
- All transactions are serialized to MsgPack format
- All transactions (both transaction log and merkle tree hash stores) are stored in LeveldDB
- One can use `read_ledger` script to get transactions for a specified ledger in readable (JSON) format
- See TBD on the roles and who can create each type of transactions

Below you can find the format and description of all supported transactions.

## Genesis transactions
Each ledger may have a number of pre-defined transaction defining the Pool and Network.
- pool genesis transactions defining initial trusted Nodes in the Pool
- domain genesis transactions defining initial trusted Trustees and Stewards


## Common metadata
Each transaction has the following metadata values common for all transaction types (see `reqToTxn` in plenum).
These values are added to each transaction as first-level keys (that is at the same level as real data).

**TODO**: consider distinguishing and separating real transaction data and metadata into different levels.    

- `type` (number as string): 

    transaction type:
    
        - NODE = "0"
        - NYM = "1"
        - ATTRIB = "100"
        - SCHEMA = "101"
        - CLAIM_DEF = "102"
        - POOL_UPGRADE = "109"
        - NODE_UPGRADE = "110"
        - POOL_CONFIG = "111"
        
- `identifier` (base58-encoded string):
 
     identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
     for 16 or 32 bit DID value.
     It may differ from `dest` field on some of transaction (for example NYM), where `dest` is target identifier (newly created DID identifier for example).
     Example: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID
     
- `reqId` (integer): 

    unique ID number of the request with transaction
    
- `signature` (base58-encoded string; mutually exclusive with `signature` field):
 
    submitter's signature
    
- `signatures` (array of base58-encoded string; mutually exclusive with `signature` field): 
    
    submitters' signature in multisig case
    
- `txnTime` (integer as POSIX timestamp): 

    the time when transaction was written to the Ledger as POSIX timestamp

Please note that all these metadata fields may be absent for genesis transactions.

## Domain Ledger

#### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and trustee can be created only by other trusties.
- `dest` (base58-encoded string):

    target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    Example: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID
     
- `role` (number as string; optional): 

    role of a user NYM record being created for. One of the following numbers
    
        - None (common USER)
        - "0" (TRUSTEE)
        - "2" (STEWARD)
        - "101" (TRUST_ANCHOR)
    
  A TRUSTEE can change any Nym's role to None, this stopping it from making any writes
  
- `verkey` (base58-encoded string; optional): 

    target verification key as base58-encoded string

- `alias` (string; optional): 

    NYM's alias

**Example**:
```
{
    "dest":"GEzcdDLhCpGCYRHW82kjHd",
    "verkey":"~HmUWn928bnFT6Ephf65YXv",
    "role":"101",
    
    "type":"1",
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1513945121191691,
    "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
    "signatures":null,
    "txnTime":1513945121
}
```

#### ATTRIB
Adds attribute to a NYM record

- `dest` (base58-encoded string):

    target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    Example: `identifier` is a DID of a Trust Anchor setting an attribute for a DID, and `dest` is the DID we set an attribute for.
    
- `raw` (sha256 hash string; mutually exclusive with `hash` and `enc`):

    Hash of a raw attribute data. Raw data is represented as json, where key is attribute name and value is it's value.
    The ledger contains hash only; the real data is stored in the attribute store.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data (as sent by the client)

- `enc` (sha256 hash string; mutually exclusive with `raw` and `hash`):

    Hash of encrypted attribute data.
    The ledger contains hash only; the real encrypted data is stored in the attribute store. 

**Example**:
```
{
    "dest":"GEzcdDLhCpGCYRHW82kjHd",
    "raw":"3cba1e3cf23c8ce24b7e08171d823fbd9a4929aafd9f27516e30699d3a42026a",
    
    "type":"1",
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1513945121191691,
    "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
    "signatures":null,
    "txnTime":1513945121
}
```


#### SCHEMA
Claim's schema
- `data` (dict):
 
     dictionary with Schema's data:
     
        - `attr_names`: array of attribute name strings
        - `name`: Schema's name string
        - `version`: Schema's vserion string

**Example**:
```
{
    "data": {
        "attr_names": ["undergrad","last_name","first_name","birth_date","postgrad","expiry_date"],
        "name":"Degree",
        "version":"1.0"
    },
    
    "type":"102"
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1514192534428527,
    "signature":"nKdn1WE1wkDdwcbaYuQZDiqHnKEDLoz14B2PFeVYTEXG4BkybnYQD2Qwg4nSUZF9J5XPXJfTyewdbeDthazWuir",
    "signatures":null,
    "txnTime":1514192534
}
```

#### CLAIM_DEF
A claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema
- `data` (dict):
 
     dictionary with Claim Definition's data:
     
        - `primary`: primary claim public key
        - `revocation`: revocation claim public key
        
- `ref` (string):
    
    Sequence number of a Schema tjis claim definition is created for

- `signature_type` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

**Example**:
```
{
    "data": {
        "primary": {
            ...
         },
        "revocation": {
            ...
        }
    },
    "ref":12,
    "signature_type":"CL",
    
    "type":"102"
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1514192534428527,
    "signature":"nKdn1WE1wkDdwcbaYuQZDiqHnKEDLoz14B2PFeVYTEXG4BkybnYQD2Qwg4nSUZF9J5XPXJfTyewdbeDthazWuir",
    "signatures":null,
    "txnTime":1514192534
}
```

## Pool Ledger

#### NODE

Adds a new node to the pool, or updates existing node in the pool

- `data` (dict):
    
    Data associated with the Node:
    
    - `alias` (string): Node's alias
    - `blskey` (base58-encoded string): BLS multi-signature key as base58-encoded string (it's needed for BLS signatures and state proofs support)
    - `client_ip` (string): Node's client listener IP address, that is the IP clients connect to the node to send read and write requests (ZMQ with TCP)  
    - `client_port` (string): Node's client listener port, that is the port clients connect to the node to send read and write requests (ZMQ with TCP)
    - `node_ip` (string): The IP address other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `node_port` (string): The port other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `services` (array of strings): the service of the Node. `VALIDATOR` is the only supported one now. 

- `dest` (base58-encoded string):

    target Node's DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the transaction submitter (Steward's DID).
    Example: `identifier` is a DID of a Steward setting creating a new Node, and `dest` is the DID of this Node.
    
- `verkey` (base58-encoded string; optional): 

    target Node verification key as base58-encoded string

**Example**:
```
{
    "data": {
        "alias":"Delta",
        "blskey":"4kkk7y7NQVzcfvY4SAe1HBMYnFohAJ2ygLeJd3nC77SFv2mJAmebH3BGbrGPHamLZMAFWQJNHEM81P62RfZjnb5SER6cQk1MNMeQCR3GVbEXDQRhhMQj2KqfHNFvDajrdQtyppc4MZ58r6QeiYH3R68mGSWbiWwmPZuiqgbSdSmweqc",
        "client_ip":"127.0.0.1",
        "client_port":7407,
        "node_ip":"127.0.0.1",
        "node_port":7406,
        "services":["VALIDATOR"]
    },
    "dest":"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2",
    
    "type":"0",
    "identifier":"WMStfRmANynUmdpa1QYKDw",
    "reqId":1514190301783582,
    "signature":"3uscTPs41aS65KvhDDLMpgL73p9AYEs2F8xo3M6G5FpH1tyuAWRq3NbJoEF55KeotBgMiXDKS27fb5Pe79R6wToo",
    "signatures":null,
    "txnTime":1514190301
}
```



## Config Ledger

#### POOL_UPGRADE
Command to upgrade the Pool (sent by Trustee)


#### NODE_UPGRADE
Status of each Node's upgrade (sent by each upgraded Node)

#### POOL_CONFIG
Command to change Pool's configuration
