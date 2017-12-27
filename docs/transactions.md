# Transactions
This doc is about supported transactions and their representation on the Ledger (that is internal one).
If you are interested in the format of client's Request (both write and read ones), then have a look at [requests](requests.md).

- All transactions are stored in distributed Ledger (replicated on all Nodes) 
- The ledger is based on Merkle Tree. 
- The ledger consists of two things:
    - transactions log as a sequence of key-value pairs 
where key is a sequence number of the transaction and value is serialized transaction
    - merkle tree (where hashes for leaves and nodes are persisted)
- Each transaction has a sequence number (no gaps) - keys in transactions log
- So, this can be considered as a blockchain where each block size equals to 1
- There are multiple ledgers by default:
    - pool ledger: transactions related to pool/network configuration (listing all nodes, their keys and addresses)
    - config ledger: transactions for pool configuration plus transactions related to Pool Upgrade
    - domain ledger: all main domain and application specific transactions (including NYM transactions for DID)
- All transactions are serialized to MsgPack format
- All transactions (both transaction log and merkle tree hash stores) are stored in LevelDB
- One can use `read_ledger` script to get transactions for a specified ledger in a readable (JSON) format
- See [roles and permissions](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0) on the roles and who can create each type of transactions

Below you can find the format and description of all supported transactions.

## Genesis transactions
As Indy is Public **Permissioned** blockchain, each ledger may have a number of pre-defined 
transactions defining the Pool and the Network.
- pool genesis transactions defining initial trusted Nodes in the Pool
- domain genesis transactions defining initial trusted Trustees and Stewards


## Common metadata
Each transaction has the following metadata values common for all transaction types (see `reqToTxn` in plenum).
These values are added to each transaction as first-level keys (that is at the same level as real data).

**TODO**: consider distinguishing and separating real transaction data and metadata into different levels.    

- `type` (enum number as string): 

    Supported transaction type:
    
        - NODE = "0"
        - NYM = "1"
        - ATTRIB = "100"
        - SCHEMA = "101"
        - CLAIM_DEF = "102"
        - POOL_UPGRADE = "109"
        - NODE_UPGRADE = "110"
        - POOL_CONFIG = "111"
        
- `identifier` (base58-encoded string):
 
     Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
     for 16 or 32 bit DID value.
     It may differ from `dest` field for some of transaction (for example NYM), where `dest` is a 
     target identifier (for example, a newly created DID identifier).
     
     *Example*: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID.
     
- `reqId` (integer): 

    Unique ID number of the request with transaction.
        
- `signature` (base58-encoded string; mutually exclusive with `signatures` field):
 
    Submitter's signature.
    
- `signatures` (array of base58-encoded string; mutually exclusive with `signature` field): 
    
    Submitters' signature in multisig case. This is a map where client's identifiers are the keys and 
    base58-encoded signature strings are the values.
    
- `txnTime` (integer as POSIX timestamp): 

    The time when transaction was written to the Ledger as POSIX timestamp.

Please note that all these metadata fields may be absent for genesis transactions.

## Domain Ledger

#### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and trustee can be created only by other trusties (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).

The transaction can be used for 
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.
 
- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID.
     
- `role` (enum number as string; optional): 

    Role of a user NYM record being created for. One of the following numbers
    
        - None (common USER)
        - "0" (TRUSTEE)
        - "2" (STEWARD)
        - "101" (TRUST_ANCHOR)
    
  A TRUSTEE can change any Nym's role to None, this stopping it from making any writes (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).
  
- `verkey` (base58-encoded string; optional): 

    Target verification key as base58-encoded string. If not set, then either the target identifier
    (`dest`) is 32-bit cryptonym CID (this is deprecated), or this is a user under guardianship
    (doesnt owns the identifier yet).

- `alias` (string; optional): 

    NYM's alias.

If there is no NYM transaction with the specified DID (`dest`), then it can be considered as creation of a new DID.

If there is a NYM transaction with the specified DID (`dest`),  then this is update of existing DID.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if key rotation needs to be performed, the owner of the DID needs to send a NYM request with
`dest` and `verkey` only. `role` and `alias` will stay the same.


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

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the submitter.
    
    *Example*: `identifier` is a DID of a Trust Anchor setting an attribute for a DID, and `dest` is the DID we set an attribute for.
    
- `raw` (sha256 hash string; mutually exclusive with `hash` and `enc`):

    Hash of the raw attribute data. 
    Raw data is represented as json, where key is attribute name and value is attribute value.
    The ledger contains hash of the raw data only; the real raw data is stored in a separate 
    attribute store.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data (as sent by the client).

- `enc` (sha256 hash string; mutually exclusive with `raw` and `hash`):

    Hash of encrypted attribute data.
    The ledger contains hash only; the real encrypted data is stored in a separate 
    attribute store. 

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
Adds Claim's schema.

It's not possible to update existing Schema.
So, if the Schema needs to be evolved, a new Schema with a new version or name needs to be created.

- `data` (dict):
 
     Dictionary with Schema's data:
     
        - `attr_names`: array of attribute name strings
        - `name`: Schema's name string
        - `version`: Schema's version string

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
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema.

- `data` (dict):
 
     Dictionary with Claim Definition's data:
     
        - `primary`: primary claim public key
        - `revocation`: revocation claim public key
        
- `ref` (string):
    
    Sequence number of a Schema transaction the claim definition is created for.

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
    - `blskey` (base58-encoded string; optional): BLS multi-signature key as base58-encoded string (it's needed for BLS signatures and state proofs support)
    - `client_ip` (string; optional): Node's client listener IP address, that is the IP clients use to connect to the node when sending read and write requests (ZMQ with TCP)  
    - `client_port` (string; optional): Node's client listener port, that is the port clients use to connect to the node when sending read and write requests (ZMQ with TCP)
    - `node_ip` (string; optional): The IP address other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `node_port` (string; optional): The port other Nodes use to communicate with this Node; no clients are allowed here (ZMQ with TCP)
    - `services` (array of strings; optional): the service of the Node. `VALIDATOR` is the only supported one now. 

- `dest` (base58-encoded string):

    Target Node's DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `identifier` metadata field, where `identifier` is the DID of the transaction submitter (Steward's DID).
    
    *Example*: `identifier` is a DID of a Steward creating a new Node, and `dest` is the DID of this Node.
    
- `verkey` (base58-encoded string; optional): 

    Target Node verification key as base58-encoded string.
    It may absent if `dest` is 32-bit cryptonym CID. 

If there is no NODE transaction with the specified Node ID (`dest`), then it can be considered as creation of a new NODE.

If there is a NODE transaction with the specified Node ID (`dest`), then this is update of existing NODE.
In this case we can specify only the values we would like to override. All unspecified values remain the same.
So, if a Steward wants to rotate BLS key, then it's sufficient to send a NODE transaction with `dest` and a new `blskey` in `data`.
There is no need to specify all other fields in `data`, and they will remain the same.


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

**Example:**
```
{
    "name":"upgrade-13",
    "action":"start",
    "version":"1.3",
    "schedule":{"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2":"2017-12-25T10:25:58.271857+00:00","AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3":"2017-12-25T10:26:16.271857+00:00","DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2":"2017-12-25T10:26:25.271857+00:00","JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ":"2017-12-25T10:26:07.271857+00:00"},
    "sha256":"db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55",
    "force":false,
    "reinstall":false,
    "timeout":1,
    "justification":null,
    
    "type":"109",
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1514197458906260,
    "signature":"5pj8EDBWXx5xDFsX9xLZzWQEGZJx1ooZxorL7JUjM1PQFTj9ZBG8Fg6zbcMacjSWkxqpRLhr9ERt2XfA4muskHNr",
    "signatures":null,
    "txnTime":1514197459,
}
```

#### NODE_UPGRADE
Status of each Node's upgrade (sent by each upgraded Node)

- `data` (dict):

    Data related to Node Upgrade:
    
    - `action`: one of `in_progress`, `complete` or `fail`
    - `version`: the version of indy-node the node was upgraded to
    

**Example:**
```
{
    "data":{
        "action":"complete",
        "version":"1.2"
    },
    
    "type":"110",
    "identifier":"DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2",
    "reqId":1514207697895141,
    "signature":"2brJa9NJzagQQfhUSNCRY1Tfthj8RdKjUx1xUm2hmnc8sWGQpHbfDGXJwWMdt8tHnPpVrnHUj1Pfaucmdpo1KKUD",
    "signatures":null,
    "txnTime":1514207698,
}
```


#### POOL_CONFIG
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
    

**Example:**
```
{
    "writes":false,
    "force":true,
    
    "type":"111",
    "identifier":"L5AD5g65TDQr1PPHHRoiGf",
    "reqId":1514194299680775,
    "signature":"5f7crPEYfVF47QSQCqRGposfrgUCQjp9YLfceqP7j9gM2m5R6mDnQUhiCiUr42cN1uSUraFFCyF1avPhNaUTcH1M",
    "signatures":null,
    "txnTime":1514194299
}
```
