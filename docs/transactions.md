# Transactions

* [General Information](#general-information)
* [Genesis Transactions](#genesis-transactions)
* [Common Metadata](#common-metadata)
* [Domain Ledger](#domain-ledger)

    * [NYM](#nym)    
    * [ATTRIB](#attrib)    
    * [SCHEMA](#schema)
    * [CLAIM_DEF](#claim_def)
    
* [Pool Ledger](#pool-ledger)    
    * [NODE](#node)
    
* [Config Ledger](#config-ledger)    
    * [POOL_UPGRADE](#pool_upgrade)
    * [NODE_UPGRADE](#node_upgrade)
    * [POOL_CONFIG](#pool_config)

## General Information

This doc is about supported transactions and their representation on the Ledger (that is internal one).
If you are interested in the format of client's Request (both write and read ones), then have a look at [requests](requests.md).

- All transactions are stored in a distributed Ledger (replicated on all Nodes) 
- The ledger is based on Merkle Tree
- The ledger consists of two things:
    - transactions log as a sequence of key-value pairs 
where key is a sequence number of the transaction and value is the serialized transaction
    - merkle tree (where hashes for leaves and nodes are persisted)
- Each transaction has a sequence number (no gaps) - keys in transactions log
- So, this can be considered as a blockchain where each block size equals to 1
- There are multiple ledgers by default:
    - *pool ledger*: transactions related to pool/network configuration (listing all nodes, their keys and addresses)
    - *config ledger*: transactions for pool configuration plus transactions related to Pool Upgrade
    - *domain ledger*: all main domain and application specific transactions (including NYM transactions for DID)
- All transactions are serialized to MsgPack format
- All transactions (both transaction log and merkle tree hash stores) are stored in LevelDB
- One can use `read_ledger` script to get transactions for a specified ledger in a readable (JSON) format
- See [roles and permissions](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0) on the roles and who can create each type of transactions

Below you can find the format and description of all supported transactions.

## Genesis Transactions
As Indy is Public **Permissioned** blockchain, each ledger may have a number of pre-defined 
transactions defining the Pool and the Network.
- pool genesis transactions defining initial trusted Nodes in the Pool
- domain genesis transactions defining initial trusted Trustees and Stewards

## Common Structure
Each transaction has the following structure containing of metadata values (common for all transaction types) and 
transaction specific data:
```
{
    "txnType": <...>,
    "txnVersion": <...>,
    
    "data": {
        <txn-specific fields>
    }
    
    "reqMetadata": {
        "reqId": <...>,
        "senderDid": <...>,
        "signature": <...>,
        "multiSignature": <...>,
    },
    
    "txnMetadata": {
        "creationTime": <...>,
        "seqNo": <...>,  
    }

}
```

- `txnType` (enum number as string): 

    Supported transaction type:
    
    - NODE = "0"
    - NYM = "1"
    - ATTRIB = "100"
    - SCHEMA = "101"
    - CLAIM_DEF = "102"
    - POOL_UPGRADE = "109"
    - NODE_UPGRADE = "110"
    - POOL_CONFIG = "111"
        
- `txnVersion` (string):

    Transaction version to be able to evolve transactions.
    The content of `data` and `reqMetadata` and `txnMetadata` fields may depend on the version.  
   
- `data` (json):

    Transaction-specific data fields (see next sections for each transaction description).   
       
- `reqMetadata` (json):

    Metadata as came from the Request.
        
    - `senderDid` (base58-encoded string):
         Identifier (DID) of the transaction submitter (client who sent the transaction) as base58-encoded string
         for 16 or 32 bit DID value.
         It may differ from `did` field for some of transaction (for example NYM), where `did` is a 
         target identifier (for example, a newly created DID identifier).
         
         *Example*: `senderDid` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
         
    - `reqId` (integer): 
        Unique ID number of the request with transaction.
            
    - `signature` (base58-encoded string; mutually exclusive with `multiSignature` field):
        Submitter's signature.
        
    - `multiSignature` (array of base58-encoded string; mutually exclusive with `signature` field): 
        Submitters' signature in multisig case. This is a map where client's identifiers are the keys and 
        base58-encoded signature strings are the values.
    
- `txnMetadata` (json):

    Metadata attached to the transaction.    
    
    - `creationTime` (integer as POSIX timestamp): 
        The time when transaction was written to the Ledger as POSIX timestamp.
        
    - `seqNo` (integer):
        A unique sequence number of the transaction on Ledger

Please note that all these metadata fields may be absent for genesis transactions.

## Domain Ledger

#### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and trustee can be created only by other trusties (see [roles](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)).

The transaction can be used for 
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.
 
- `did` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `submitterId` metadata field, where `senderDid` is the DID of the submitter.
    
    *Example*: `senderDid` is a DID of a Trust Anchor creating a new DID, and `did` is a newly created DID.
     
- `role` (enum number as string; optional): 

    Role of a user NYM record being created for. One of the following numbers
    
    - None (common USER)
    - "0" (TRUSTEE)
    - "2" (STEWARD)
    - "101" (TRUST_ANCHOR)
    
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


**Example**:
```
{
    "txnType":"1",
    
    "data": {
        "did":"GEzcdDLhCpGCYRHW82kjHd",
        "verkey":"~HmUWn928bnFT6Ephf65YXv",
        "role":"101",
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,  
    },

}
```

#### ATTRIB
Adds attribute to a NYM record

- `did` (base58-encoded string):

    Target DID we set an attribute for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `senderDid` metadata field, where `senderDid` is the DID of the submitter.
    
    *Example*: `senderDid` is a DID of a Trust Anchor setting an attribute for a DID, and `did` is the DID we set an attribute for.
    
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
    "txnType":"100",
    
    "data": {
        "did":"GEzcdDLhCpGCYRHW82kjHd",
        "raw":"3cba1e3cf23c8ce24b7e08171d823fbd9a4929aafd9f27516e30699d3a42026a",
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
}
```


#### SCHEMA
Adds Claim's schema.

It's not possible to update existing Schema.
So, if the Schema needs to be evolved, a new Schema with a new version or name needs to be created.

- `did` (base58-encoded string):

    Target DID we create a Schema for as base58-encoded string for 16 or 32 bit DID value.
    It differs from `senderDid` metadata field, where `senderDid` is the DID of the submitter.
    In practice, `did` will be equal to `senderDid` in most of the cases.
    
    *Example*: `senderDid` is a DID of a Trust Anchor setting an attribute for a DID, and `did` is the DID we create the Schema for.

- `attrNames` (array of strings):
 
    Array of attribute name strings.

- `name` (string):
 
    Schema's name string.

- `version` (string):
 
    Schema's version string

**Example**:
```
{
    "txnType":"101",
    
    "data": {
        "did":"L5AD5g65TDQr1PPHHRoiGf",
        "attrNames": ["undergrad","last_name","first_name","birth_date","postgrad","expiry_date"],
        "name":"Degree",
        "version":"1.0",
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
}
```

#### CLAIM_DEF
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular Claim Schema.

It's not possible to update `data` in existing Claim Def.
So, if a Claim Def needs to be evolved (for example, a key needs to be rotated), then
a new Claim Def needs to be created for a new Issuer DID (`did`).

- `did` (base58-encoded string):

    Target DID we create a Claim Def for (that is Issuer DID) as base58-encoded string for 16 or 32 bit DID value.
    It differs from `senderDid` metadata field, where `senderDid` is the DID of the submitter.
    In practice, `did` will be equal to `senderDid` in most of the cases. 
    
    *Example*: `senderDid` is a DID of a Trust Anchor setting an attribute for a DID, and `did` is the DID we create the Claim Def for.


- `publicKeys` (dict):
 
     Dictionary with Claim Definition's public keys:
     
    - `primary`: primary claim public key
    - `revocation`: revocation claim public key
        
- `schemaRef` (string):
    
    Sequence number of a Schema transaction the claim definition is created for.

- `signatureType` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

**Example**:
```
{
    "txnType":"102",
    
    "data": {
        "did":"L5AD5g65TDQr1PPHHRoiGf",
        "publicKeys": {
            "primary": {
                ...
             },
            "revocation": {
                ...
            }
        },
        "schemaRef":12,
        "signatureType":"CL",
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
}
```

## Pool Ledger

#### NODE

Adds a new node to the pool, or updates existing node in the pool

- `did` (base58-encoded string):

    Target Node's DID as base58-encoded string for 16 or 32 bit DID value.
    It differs from `senderDid` metadata field, where `senderDid` is the DID of the transaction submitter (Steward's DID).
    
    *Example*: `senderDid` is a DID of a Steward creating a new Node, and `did` is the DID of this Node.
    
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


**Example**:
```
{
    "txnType":"0",

    "data": {
        "did":"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2",
        "alias":"Delta",
        "blskey":"4kkk7y7NQVzcfvY4SAe1HBMYnFohAJ2ygLeJd3nC77SFv2mJAmebH3BGbrGPHamLZMAFWQJNHEM81P62RfZjnb5SER6cQk1MNMeQCR3GVbEXDQRhhMQj2KqfHNFvDajrdQtyppc4MZ58r6QeiYH3R68mGSWbiWwmPZuiqgbSdSmweqc",
        "clientIp":"127.0.0.1",
        "clientPort":7407,
        "nodeIp":"127.0.0.1",
        "nodePort":7406,
        "services":["VALIDATOR"]
    },

    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
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
    "txnType":"109",
    
    "data"" {
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
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
}
```

#### NODE_UPGRADE
Status of each Node's upgrade (sent by each upgraded Node)

- `action` (enum string): 

    One of `in_progress`, `complete` or `fail`.
    
- `version` (string): 
    
    The version of indy-node the node was upgraded to.
    

**Example:**
```
{
    "txnType":"110",
    
    "data":{
        "action":"complete",
        "version":"1.2"
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
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
    "txnType":"111",
    
    "data": {
        "writes":false,
        "force":true,
    },
    
    "reqMetadata": {
        "reqId":1513945121191691,
        "senderDid":"L5AD5g65TDQr1PPHHRoiGf",
        "signature":"3SyRto3MGcBy1o4UmHoDezy1TJiNHDdU9o7TjHtYcSqgtpWzejMoHDrz3dpT93Xe8QXMF2tJVCQTtGmebmS2DkLS",
        "multiSignature":null,
    },
    "txnMetadata": {
        "creationTime":1513945121,
        "seqNo": 10,
    },
}
```
