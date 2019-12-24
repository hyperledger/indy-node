# Transactions

* [General Information](#general-information)
* [Genesis Transactions](#genesis-transactions)
* [Common Structure](#common-structure)
* [Domain Ledger](#domain-ledger)

    * [NYM](#nym)
    * [ATTRIB](#attrib)
    * [SCHEMA](#schema)
    * [CLAIM_DEF](#claim_def)
    * [REVOC_REG_DEF](#revoc_reg_def)
    * [REVOC_REG_ENTRY](#revoc_reg_entry)
    * [SET_CONTEXT](#set_context)

* [Pool Ledger](#pool-ledger)
    * [NODE](#node)

* [Config Ledger](#config-ledger)
    * [POOL_UPGRADE](#pool_upgrade)
    * [NODE_UPGRADE](#node_upgrade)
    * [POOL_CONFIG](#pool_config)
    * [AUTH_RULE](#auth_rule)
    * [AUTH_RULES](#auth_rules)
    * [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)
    * [TRANSACTION_AUTHOR_AGREEMENT_AML](#transaction_author_agreement_AML)
    * [TRANSACTION_AUTHOR_AGREEMENT_DISABLE](#transaction_author_agreement_disable)
    
* [Actions](#actions)
    * [POOL_RESTART](#pool_restart)    

## General Information

This doc is about supported transactions and their representation on the Ledger (that is, the internal one).
If you are interested in the format of a client's request (both write and read), then have a look at [requests](requests.md).

- All transactions are stored in a distributed ledger (replicated on all nodes)
- The ledger is based on a [Merkle Tree](https://en.wikipedia.org/wiki/Merkle_tree)
- The ledger consists of two things:
    - transactions log as a sequence of key-value pairs
where key is a sequence number of the transaction and value is the serialized transaction
    - merkle tree (where hashes for leaves and nodes are persisted)
- Each transaction has a sequence number (no gaps) - keys in transactions log
- So, this can be considered a blockchain where each block's size is equal to 1
- There are multiple ledgers by default:
    - *pool ledger*: transactions related to pool/network configuration (listing all nodes, their keys and addresses)
    - *config ledger*: transactions for pool configuration plus transactions related to pool upgrade
    - *domain ledger*: all main domain and application specific transactions (including NYM transactions for DID)
- All transactions are serialized to MsgPack format
- All transactions (both transaction log and merkle tree hash stores) are stored in a LevelDB
- One can use the `read_ledger` script to get transactions for a specified ledger in a readable format (JSON)
- See [roles and permissions](auth_rules.md) for a list of roles and they type of transactions they can create.
    
Below you can find the format and description of all supported transactions.

## Genesis Transactions
As Indy is a public **permissioned** blockchain, each ledger may have a number of pre-defined
transactions defining the initial pool and network.
- pool genesis transactions define initial trusted nodes in the pool
- domain genesis transactions define initial trusted trustees and stewards

## Common Structure
Each transaction has the following structure consisting of metadata values (common for all transaction types) and
transaction specific data:
```
{
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
}
```
- `ver` (string):

    Transaction version to be able to evolve content.
    The content of all sub-fields may depend on this version.

- `txn` (dict):

    Transaction-specific payload (data)

    - `type` (enum number as string):

        Supported transaction types:

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
        - AUTH_RULES = "122"
        - SET_CONTEXT = "200"

    - `protocolVersion` (integer; optional):

        The version of client-to-node or node-to-node protocol. Each new version may introduce a new feature in requests/replies/data.
        Since clients and different nodes may be at different versions, we need this field to support backward compatibility
        between clients and nodes.

    - `data` (dict):

        Transaction-specific data fields (see following sections for each transaction's description).

    - `metadata` (dict):

        Metadata as came from the request.

        - `from` (base58-encoded string):
         
             Identifier (DID) of the transaction author as base58-encoded string
             for 16 or 32 bit DID value.
             It may differ from `endorser` field who submits the transaction on behalf of `identifier`.
             If `endorser` is absent, then the author (`identifier`) plays the role of endorser and submits request by his own.
             It also may differ from `dest` field for some of requests (for example NYM), where `dest` is a target identifier (for example, a newly created DID identifier).
             
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
            
            - `taaDigest` (SHA256 hex digest string): SHA256 hex digest of the latest Transaction Author Agreement on the ledger. The digest is calculated from concatenation of [TRANSACTION_AUTHOR_AGREEMENT](#transaction_author_agreement)'s `version` and `text`.
            
            - `mechanism` (string): a mechanism used to accept the signature; must be present in the latest list of transaction author agreement acceptane mechanisms on the ledger  
            
            - `time` (integer as POSIX timestamp): transaction author agreement acceptance time. The time needs to be rounded to date to prevent correlation of different transactions which is possible when acceptance time is too precise.
                
    - `txnMetadata` (dict):

        Metadata attached to the transaction.

         - `version` (integer):
            Transaction version to be able to evolve `txnMetadata`.
            The content of `txnMetadata` may depend on the version.

        - `txnTime` (integer as POSIX timestamp):
            The time when transaction was written to the Ledger as POSIX timestamp.

        - `seqNo` (integer):
            A unique sequence number of the transaction on Ledger

        - `txnId` (string, optional):
            Txn ID as State Trie key (address or descriptive data). It must be unique within the ledger. Usually present for Domain transactions only.


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

Please note that all these metadata fields may be absent for genesis transactions.

## Domain Ledger

#### NYM
Creates a new NYM record for a specific user, endorser, steward or trustee.
Note that only trustees and stewards can create new endorsers and a trustee can be created only by other trustees (see [roles](auth_rules.md)).

The transaction can be used for
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It may differ from the `from` metadata field, where `from` is the DID of the submitter.
    If they are equal (in permissionless case), then transaction must be signed by the newly created `verkey`.

    *Example*: `from` is a DID of a Endorser creating a new DID, and `dest` is a newly created DID.

- `role` (enum number as integer; optional):

    Role of a user that the NYM record is being created for. One of the following values

    - None (common USER)
    - "0" (TRUSTEE)
    - "2" (STEWARD)
    - "101" (ENDORSER)
    - "201" (NETWORK_MONITOR)
    
  A TRUSTEE can change any Nym's role to None, thus stopping it from making any further writes (see [roles](auth_rules.md)).

- `verkey` (base58-encoded string, possibly starting with "~"; optional):

    Target verification key as base58-encoded string. It can start with "~", which means that
    it's an abbreviated verkey and should be 16 bytes long when decoded, otherwise it's a full verkey
    which should be 32 bytes long when decoded. If not set, then either the target identifier
    (`did`) is 32-bit cryptonym CID (this is deprecated), or this is a user under guardianship
    (doesn't own the identifier yet).
    Verkey can be changed to "None" by owner, it means that this user goes back under guardianship.

- `alias` (string; optional):

    NYM's alias.

If there is no NYM transaction for the specified DID (`did`) yet, then this can be considered as the creation of a new DID.

If there is already a NYM transaction with the specified DID (`did`),  then this is is considered an update of that DID.
In this case **only the values that need to be updated should be specified** since any specified one is treated as an update even if it matches the current value in ledger. All unspecified values remain unchanged.

So, if key rotation needs to be performed, the owner of the DID needs to send a NYM request with
`did` and `verkey` only. `role` and `alias` will stay the same.


**Example**:
```
{
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

}
```

#### ATTRIB
Adds an attribute to a NYM record


- `dest` (base58-encoded string):

    Target DID we set an attribute for as base58-encoded string for 16 or 32 byte DID value.
    It differs from `from` metadata field, where `from` is the DID of the submitter.

    *Example*: `from` is a DID of a Endorser setting an attribute for a DID, and `dest` is the DID we set an attribute for.

- `raw` (sha256 hash string; mutually exclusive with `hash` and `enc`):

    Hash of the raw attribute data.
    Raw data is represented as JSON, where the key is the attribute name and the value is the attribute value.
    The ledger only stores a hash of the raw data; the real (unhashed) raw data is stored in a separate
    attribute store.

- `hash` (sha256 hash string; mutually exclusive with `raw` and `enc`):

    Hash of attribute data (as sent by the client).
    The ledger stores this hash; nothing is stored in an attribute store.

- `enc` (sha256 hash string; mutually exclusive with `raw` and `hash`):

    Hash of encrypted attribute data.
    The ledger contains the hash only; the real encrypted data is stored in a separate
    attribute store.

**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":"100",
        "protocolVersion":2,

        "data": {
            "ver":1,
            "dest":"GEzcdDLhCpGCYRHW82kjHd",
            "raw":"3cba1e3cf23c8ce24b7e08171d823fbd9a4929aafd9f27516e30699d3a42026a",
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
        "txnId": "N22KY2Dyvmuu2PyyqSFKue|02"
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```


#### SCHEMA
Adds a Claim's schema.

It's not possible to update an existing schema.
So, if the Schema needs to be evolved, a new Schema with a new version or new name needs to be created.

- `data` (dict):

     Dictionary with Schema's data:

    - `attr_names`: array of attribute name strings
    - `name`: Schema's name string
    - `version`: Schema's version string


**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":101,
        "protocolVersion":2,

        "data": {
            "ver":1,
            "data": {
                "attr_names": ["undergrad","last_name","first_name","birth_date","postgrad","expiry_date"],
                "name":"Degree",
                "version":"1.0"
            },
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "endorser": "D6HG5g65TDQr1PPHHRoiGf",
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
        "txnId":"L5AD5g65TDQr1PPHHRoiGf1|Degree|1.0",
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }

}
```

#### CLAIM_DEF
Adds a claim definition (in particular, public key), that Issuer creates and publishes for a particular claim schema.

- `data` (dict):

     Dictionary with claim definition's data:

    - `primary` (dict): primary claim public key
    - `revocation` (dict): revocation claim public key

- `ref` (string):

    Sequence number of a schema transaction the claim definition is created for.

- `signature_type` (string):

    Type of the claim definition (that is claim signature). `CL` (Camenisch-Lysyanskaya) is the only supported type now.

- `tag` (string, optional):

    A unique tag to have multiple public keys for the same Schema and type issued by the same DID.
    A default tag `tag` will be used if not specified.

**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":102,
        "protocolVersion":2,

        "data": {
            "ver":1,
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
            'tag': 'some_tag'
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "endorser": "D6HG5g65TDQr1PPHHRoiGf",
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
        "txnId":"HHAD5g65TDQr1PPHHRoiGf2L5AD5g65TDQr1PPHHRoiGf1|Degree1|CL|key1",
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### REVOC_REG_DEF
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

**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":113,
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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "endorser": "D6HG5g65TDQr1PPHHRoiGf",
            'digest': '4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453',
            'payloadDigest': '21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685',
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
        "txnId":"L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1",
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### REVOC_REG_ENTRY
The RevocReg entry containing the new accumulator value and issued/revoked indices. This is just a delta of indices, not the whole list. So, it can be sent each time a new claim is issued/revoked.

- `value` (dict):

     Dictionary with revocation registry's data:
     
     - `accum` (string): the current accumulator value
     - `prevAccum` (string): the previous accumulator value; it's compared with the current value, and txn is rejected if they don't match; it's needed to avoid dirty writes and updates of accumulator.
     - `issued` (list of integers): an array of issued indices (may be absent/empty if the type is ISSUANCE_BY_DEFAULT); this is delta; will be accumulated in state.
     - `revoked` (list of integers):  an array of revoked indices (delta; will be accumulated in state)    

- `revocRegDefId` (string): The corresponding Revocation Registry Definition's unique identifier (a key from state trie is currently used)
- `revocDefType` (string enum): Revocation Type. `CL_ACCUM` (Camenisch-Lysyanskaya Accumulator) is the only supported type now.


**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":114,
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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "endorser": "D6HG5g65TDQr1PPHHRoiGf",
            'digest': '4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453',
            'payloadDigest': '21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685',
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
        "txnId":"5:L5AD5g65TDQr1PPHHRoiGf:3:FC4aWomrA13YyvYC1Mxw7:3:CL:14:some_tag:CL_ACCUM:tag1",
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```


#### SET_CONTEXT
Adds a Context

It's not possible to update an existing Context.
If the Context needs to be evolved, a new Context with a new version or new name needs to be created.

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


**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":200,
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
                "type": "ctx
            },
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "endorser": "D6HG5g65TDQr1PPHHRoiGf",
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
        "txnId":"L5AD5g65TDQr1PPHHRoiGf1|Degree|1.0",
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

## Pool Ledger

#### NODE

Adds a new node to the pool or updates an existing node in the pool

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
So, if a Steward wants to rotate BLS key, then it's sufficient to send a NODE transaction with `dest` and a new `blskey`.
There is no need to specify all other fields, and they will remain the same.


**Example**:
```
{
    "ver": 1,
    "txn": {
        "type":0,
        "protocolVersion":2,

        "data": {
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
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest": "4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest": "4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
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
    "ver":1,
    "txn": {
        "type":110,
        "protocolVersion":2,

        "data": {
            "ver":1,
            "action":"complete",
            "version":"1.2"
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest": "4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest": "4ba05d9b2c27e52aa8778708fb4b3e5d7001eecd02784d8e311d27b9090d9453",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### AUTH_RULE

A command to change authentication rules. 
Internally authentication rules are stored as a key-value dictionary: `{action} -> {auth_constraint}`.

The list of actions is static and can be found in [auth_rules.md](auth_rules.md).
There is a default Auth Constraint for every action (defined in [auth_rules.md](auth_rules.md)). 

The `AUTH_RULE` command allows to change the Auth Constraint.
So, it's not possible to register new actions by this command. But it's possible to override authentication constraints (values) for the given action.

Please note, that list elements of `GET_AUTH_RULE` output can be used as an input (with a required changes) for `AUTH_RULE`.

The following input parameters must match an auth rule from the [auth_rules.md](auth_rules.md):
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
            
            - 'ROLE': a constraint defining how many siganatures of a given role are required
            - 'OR': logical disjunction for all constraints from `auth_constraints` 
            - 'AND': logical conjunction for all constraints from `auth_constraints`
            
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


**Example:**

Let's consider an example of changing a value of a NODE transaction's `service` field from `[VALIDATOR]` to `[]` (demotion of a node).
 We are going to set an Auth Constraint, so that the action can be only be done by two TRUSTEE or one STEWARD who is the owner (the original creator) of this transaction.

```
{  
   'txn':{  
      'type':'120',
      'protocolVersion':2,
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
      'metadata':{  
         'reqId':252174114,
         'from':'M9BJDuS24bqbJNvBRsoGg3',
         'digest':'6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c',
         'payloadDigest': '21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685',
      }
   },
   'txnMetadata':{  
      'txnTime':1551785798,
      'seqNo':1
   },   
   'reqSignature':{  
      'type':'ED25519',
      'values':[  
         {  
            'value':'4wpLLAtkT6SeiKEXPVsMcCirx9KvkeKKd11Q4VsMXmSv2tnJrRw1TQKFyov4m2BuPP4C5oCiZ6RUwS9w3EPdywnz',
            'from':'M9BJDuS24bqbJNvBRsoGg3'
         }
      ]
   },
   'ver':'1'
}
```

#### AUTH_RULES

A command to set multiple AUTH_RULEs by one transaction. 
Transaction AUTH_RULES is not divided into a few AUTH_RULE transactions, and is written to the ledger with one transaction with the full set of rules that come in the request.
Internally authentication rules are stored as a key-value dictionary: `{action} -> {auth_constraint}`.

The list of actions is static and can be found in [auth_rules.md](auth_rules.md).
There is a default Auth Constraint for every action (defined in [auth_rules.md](auth_rules.md)). 

The `AUTH_RULES` command allows to change the Auth Constraints.
So, it's not possible to register new actions by this command. But it's possible to override authentication constraints (values) for the given action.

Please note, that list elements of `GET_AUTH_RULE` output can be used as an input (with a required changes) for the field `rules` in `AUTH_RULES`.

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
            
            - 'ROLE': a constraint defining how many siganatures of a given role are required
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

**Example:**

```
{  
   'txn':{  
      'type':'120',
      'protocolVersion':2,
      'data':{
        rules: [
           {'auth_type': '0', 
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
          ...
        ]
      'metadata':{  
         'reqId':252174114,
         'from':'M9BJDuS24bqbJNvBRsoGg3',
         'digest':'6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c',
         'payloadDigest': '21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685',
      }
   },
   'txnMetadata':{  
      'txnTime':1551785798,
      'seqNo':1
   },   
   'reqSignature':{  
      'type':'ED25519',
      'values':[  
         {  
            'value':'4wpLLAtkT6SeiKEXPVsMcCirx9KvkeKKd11Q4VsMXmSv2tnJrRw1TQKFyov4m2BuPP4C5oCiZ6RUwS9w3EPdywnz',
            'from':'M9BJDuS24bqbJNvBRsoGg3'
         }
      ]
   },
   'ver':'1'
}
```

#### TRANSACTION_AUTHOR_AGREEMENT

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

    Transaction Author Agreement ratification timestamp as POSIX timestamp. May have any precision up to seconds.
    Must be specified when creating a new Agreement.
    Should be either omitted or equal to existing value in case of updating an existing Agreement (setting `retirement_ts`).

- `retirement_ts` (integer as POSIX timestamp; optional):

    Transaction Author Agreement retirement timestamp as POSIX timestamp. May have any precision up to seconds.
    Can be any timestamp either in future or in the past (the Agreement will be retired immediately in the latter case).
    Must be omitted when creating a new (latest) Agreement.
    Should be used for updating (deactivating) non-latest Agreement on the ledger.


**New Agreement Example:**
```
{
    "ver": 2,
    "txn": {
        "type":4,
        "protocolVersion":2,

        "data": {
            "ver": 2,
            "version": "1.0",
            "text": "Please read carefully before writing anything to the ledger",
            "ratification_ts": 1514304094738044
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
            "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
        },
    },
    "txnMetadata": {
        "txnTime":1577836799,
        "seqNo": 10,
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```


**Retire Agreement Example:**
```
{
    "ver": 2,
    "txn": {
        "type":4,
        "protocolVersion":2,

        "data": {
            "ver": 2,
            "version": "1.0",
            "retirement_ts": 1515415195838044
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
            "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
        },
    },
    "txnMetadata": {
        "txnTime":1577836799,
        "seqNo": 10,
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### TRANSACTION_AUTHOR_AGREEMENT_AML

Setting a list of acceptance mechanisms for transaction author agreement.

Each write request for which a transaction author agreement needs to be accepted must point to a  mechanism from the latest list on the ledger. The chosen mechanism is signed by the write request author (together with the transaction author agreement digest). 


Each acceptance mechanisms list has a unique version.

- `version` (string):

    Unique version of the transaction author agreement acceptance mechanisms list


- `aml` (dict):

    Acceptance mechanisms list data in the form `<acceptance mechanism label>: <acceptance mechanism description>`
    
- `amlContext` (string, optional):

    A context information about Acceptance mechanisms list (may be URL to external resource).   
    
    
**Example:**
```
{
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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### TRANSACTION_AUTHOR_AGREEMENT_DISABLE

Immediately retires all active Transaction Author Agreements at once by setting current timestamp as a retirement one.

It's not possible to re-enable an Agreement right after disabling all agreements because there is no active latest Agreement at this point.
A new Agreement needs to be sent instead.

**Example:**
```
{
    "ver": 1,
    "txn": {
        "type":8,
        "protocolVersion":2,

        "data": {
            "ver": 1,
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
            "digest":"6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c",
            "payloadDigest": "21f0f5c158ed6ad49ff855baf09a2ef9b4ed1a8015ac24bccc2e0106cd905685",
        },
    },
    "txnMetadata": {
        "txnTime":1577836799,
        "seqNo": 10,
    },
    "reqSignature": {
        "type": "ED25519",
        "values": [{
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

## Actions

The actions are not written to the Ledger, so this is not a transaction, just a command.

#### POOL_RESTART
POOL_RESTART is the command to restart all nodes at the time specified in field "datetime"(sent by Trustee).

- `datetime` (string):

    Restart time in datetime frmat/
    To restart as early as possible, send message without the "datetime" field or put in it value "0" or ""(empty string) or the past date on this place.
    The restart is performed immediately and there is no guarantee of receiving an answer with Reply.


- `action` (enum: `start` or `cancel`):

    Starts or cancels the Restart.

**Example:**
```
{
     "reqId": 98262,
     "type": "118",
     "identifier": "M9BJDuS24bqbJNvBRsoGg3",
     "datetime": "2018-03-29T15:38:34.464106+00:00",
     "action": "start"
}
```
