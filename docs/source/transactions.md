# Transactions

* [General Information](#general-information)
* [Genesis Transactions](#genesis-transactions)
* [Common Structure](#common-structure)
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
    * [AUTH_RULE](#auth_rule)

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
}
```
- `ver` (string):

    Transaction version to be able to evolve content.
    The content of all sub-fields may depend on this version.

- `txn` (dict):

    Transaction-specific payload (data)

    - `type` (enum number as string):

        Supported transaction types:

        - NODE = 0
        - NYM = 1
        - ATTRIB = 100
        - SCHEMA = 101
        - CLAIM_DEF = 102
        - POOL_UPGRADE = 109
        - NODE_UPGRADE = 110
        - POOL_CONFIG = 111

    - `protocolVersion` (integer; optional):

        The version of client-to-node or node-to-node protocol. Each new version may introduce a new feature in requests/replies/data.
        Since clients and different nodes may be at different versions, we need this field to support backward compatibility
        between clients and nodes.

    - `data` (dict):

        Transaction-specific data fields (see following sections for each transaction's description).

    - `metadata` (dict):

        Metadata as came from the request.

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

         - `version` (integer):
            Transaction version to be able to evolve `txnMetadata`.
            The content of `txnMetadata` may depend on the version.

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

Please note that all these metadata fields may be absent for genesis transactions.

## Domain Ledger

#### NYM
Creates a new NYM record for a specific user, trust anchor, steward or trustee.
Note that only trustees and stewards can create new trust anchors and a trustee can be created only by other trustees (see [roles](auth_rules.md)).

The transaction can be used for
creation of new DIDs, setting and rotation of verification key, setting and changing of roles.

- `dest` (base58-encoded string):

    Target DID as base58-encoded string for 16 or 32 byte DID value.
    It differs from the `from` metadata field, where `from` is the DID of the submitter.

    *Example*: `from` is a DID of a Trust Anchor creating a new DID, and `dest` is a newly created DID.

- `role` (enum number as integer; optional):

    Role of a user that the NYM record is being created for. One of the following values

    - None (common USER)
    - 0 (TRUSTEE)
    - 2 (STEWARD)
    - 101 (TRUST_ANCHOR)

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
        "protocolVersion":1,

        "data": {
            "ver": 1,
            "dest":"GEzcdDLhCpGCYRHW82kjHd",
            "verkey":"~HmUWn928bnFT6Ephf65YXv",
            "role":101,
        },

        "metadata": {
            "reqId":1513945121191691,
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

    *Example*: `from` is a DID of a Trust Anchor setting an attribute for a DID, and `dest` is the DID we set an attribute for.

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
        "protocolVersion":1,

        "data": {
            "ver":1,
            "dest":"GEzcdDLhCpGCYRHW82kjHd",
            "raw":"3cba1e3cf23c8ce24b7e08171d823fbd9a4929aafd9f27516e30699d3a42026a",
        },

        "metadata": {
            "reqId":1513945121191691,
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
        "protocolVersion":1,

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

It's not possible to update `data` in an existing claim definition.
Therefore if an existing claim definition needs to be evolved (for example, a key needs to be rotated), a new claim definition needs to be created for a new Issuer DID (`did`).

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
        "protocolVersion":1,

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
        "protocolVersion":1,

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
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
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
        "protocolVersion":1,

        "data": {
            "ver":1,
            "action":"complete",
            "version":"1.2"
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
        },
    },
    "txnMetadata": {
        "txnTime":1513945121,
        "seqNo": 10,
        "txnId":"upgrade-13",
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
        "protocolVersion":1,

        "data": {
            "ver":1,
            "writes":false,
            "force":true,
        },

        "metadata": {
            "reqId":1513945121191691,
            "from":"L5AD5g65TDQr1PPHHRoiGf",
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
            "from": "L5AD5g65TDQr1PPHHRoiGf",
            "value": "4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd"
        }]
    }
}
```

#### AUTH_RULE

Transaction to change authentication rules. 
Authentication rules are stored in the State as key - value dictionary. This coincides with the storage structure in (auth_map)[auth_rule.md]. 
If config ledger does not have a transaction for a given key, then a default rule defined in code is used.
Key - some action in the format `prefix--txn_type--field--old_value--new_value`
- `prefix` (enum: `ADD` or `EDIT`)
- `txn_type` (string) - The type of transaction to change rights to. (Example: "0", "1", ...)
- `field` (string) Change the rights to edit(add) some values from field.
- `old_value` (string; optional) Old value of field, which can be changed to a new_value.
- `new_value` (string) New value that can be used to fill the field.
Value is a set of constraints on the execution of this action. There are two types of constraints:
- AuthConstraint with `constraint_id = ROLE_CONSTRAINT_ID` and format `{constraint_id, role, sig_count, need_to_be_owner, metadata}`;
- AuthConstraintOr with `constraint_id = OR_CONSTRAINT_ID` and `auth_constraints` - list of constraints;
- AuthConstraintAnd with `constraint_id = AND_CONSTRAINT_ID` and `auth_constraints` - list of constraints;
That is, the entry 
```
"EDIT--NODE--services--[VALIDATOR]--[]" -> {constraint_id: OR,
                                            auth_constraints: [{constraint_id: ROLE,
                                                                role: STEWARD, 
                                                                sig_count: 1, 
                                                                need_to_be_owner: True},
                                                               {constraint_id: ROLE,
                                                                role: TRUSTEE, 
                                                                sig_count: 1, 
                                                                need_to_be_owner: False}
                                                               ]
                                           }
                                                                 
```
means that change the value of node services from [VALIDATOR] to [] (demotion of node) can only TRUSTEE or STEWARD if it is owner of this transaction.

**AbstractAuthConstraint:**

AuthConstraintAnd, AuthConstraintOr

- `constraint_id` (enum: `AND` or `OR`):

    Type of a constraint class. It's needed to determine a type of constraint for correct deserialization.
    - `AND` logical conjunction for all constraints from `auth_constraints` - AuthConstraintAnd
    - `OR` logical disjunction for all constraints from `auth_constraints` - AuthConstraintOr
    
- `auth_constraints` (list of ConstraintType):

    List of ConstraintType (ConstraintList or ConstraintEntity) objects
    
 ```
{ 'constraint_id': 'AND',
  'auth_constraints': [<ConstraintEntity>,
                      <ConstraintEntity>]
}
```
    
AuthConstraint

- `constraint_id` (enum: `ROLE`):

      Type of a constraint. As of now only ROLE is supported, but plugins can register new ones. It's needed to determine a type of constraint for correct deserialization.
        
- `role` (enum number as string; optional):

    Role of a user that the NYM record is being created for. One of the following values

    - None (common USER)
    - 0 (TRUSTEE)
    - 2 (STEWARD)
    - 101 (TRUST_ANCHOR)
   
- `sig_count` (int):

    The number of signatures that is needed to do the action described in the transaction fields.
    
- `need_to_be_owner` (boolean):

    Flag to check if the user must be owner of a transaction (Example: A steward must be the owner of the node to make changes to it).
    
- `metadata` (dict; optional):

    Dictionary for additional parameters of the constraint. Can be used by plugins to add additional restrictions.

```
{
    'sig_count': 1, 
    'need_to_be_owner': False, 
    'constraint_id': 'ROLE', 
    'metadata': {}, 
    'role': '0'
}
```

**Example:**
```
{  
   'txnMetadata':{  
      'txnTime':1551785798,
      'seqNo':1
   },
   'txn':{  
      'type':'120',
      'protocolVersion':2,
      'data':{  
         'constraint':{  
            'constraint_id':'ROLE',
            'need_to_be_owner':False,
            'role':'0',
            'sig_count':1,
            'metadata':{  

            }
         },
         'auth_type':'1',
         'new_value':'101',
         'field':'role',
         'auth_action':'ADD'
      },
      'metadata':{  
         'reqId':252174114,
         'digest':'6cee82226c6e276c983f46d03e3b3d10436d90b67bf33dc67ce9901b44dbc97c',
         'from':'M9BJDuS24bqbJNvBRsoGg3'
      }
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


## Action Transactions

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
