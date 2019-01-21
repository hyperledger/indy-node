# Current implemented rules in auth_map
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
| NYM              |`role` |`<empty>`       | TRUSTEE   | TRUSTEE|Adding new TRUSTEE|
| NYM              |`role` |`<empty>`       | STEWARD   | TRUSTEE|Adding new STEWARD|
| NYM              |`role` |`<empty>`       | TRUST_ANCHOR| TRUSTEE, STEWARD|Adding new TRUST_ANCHOR|
| NYM              |`role` |`<empty>`       | NETWORK_MONITOR| TRUSTEE, STEWARD|Adding new NETWORK_MONITOR|
| NYM              |`role` |`<empty>`       |`<empty>`  | TRUSTEE, STEWARD, TRUST_ANCHOR| Adding new Identity Owner|
| NYM              |`role` | TRUSTEE        |`<empty>`  | TRUSTEE | Blacklisting Trustee|
| NYM              |`role` | STEWARD        |`<empty>`  | TRUSTEE | Blacklisting Steward|
| NYM              |`role` | TRUST_ANCHOR   |`<empty>`  | TRUSTEE | Blacklisting Trust anchor|
| NYM              |`role` | NETWORK_MONITOR|`<empty>`  | TRUSTEE, STEWARD | Blacklisting user with NETWORK_MONITOR role| 
| NYM              |`verkey`|`*`|`*`| Owner of this nym | Key Rotation|
| SCHEMA           |`*`|`*`|`*`| TRUSTEE, STEWARD, TRUST_ANCHOR | Adding new Schema|
| SCHEMA           |`*`|`*`|`*`| No one can edit existing Schema | Editing Schema|
| CLAIM_DEF        |`*`|`*`|`*`| TRUSTEE, STEWARD, TRUST_ANCHOR| Adding new CLAIM_DEF transaction|
| CLAIM_DEF        |`*`|`*`|`*`| Owner of claim_def txn| Editing CLAIM_DEF transaction|
| NODE             |`services`|`<empty>`|`[VALIDATOR]`| STEWARD if it is owner of this transaction| Adding new node to pool|
| NODE             |`services`|`[VALIDATOR]`|`[]`| TRUSTEE, STEWARD if it is owner of this transaction| Demotion of node|
| NODE             |`services`|`[]`|`[VALIDATOR]`| TRUSTEE, STEWARD if it is owner of this transaction| Promotion of node|
| NODE             |`node_ip`|`*`|`*`| STEWARD if it is owner of this transaction| Changing Node's ip address|
| NODE             |`node_port`|`*`|`*`| STEWARD if it is owner of this transaction| Changing Node's port|
| NODE             |`client_ip`|`*`|`*`| STEWARD if it is owner of this transaction| Changing Client's ip address| 
| NODE             |`client_port`|`*`|`*`| STEWARD if it is owner of this transaction| Changing Client's port|
| NODE             |`blskey`|`*`|`*`| STEWARD if it is owner of this transaction| Changing Node's blskey|
| POOL_UPGRADE     |`action`|`<empty>`|`start`|TRUSTEE| Starting upgrade procedure|
| POOL_UPGRADE     |`action`|`start`|`cancel`|TRUSTEE| Canceling upgrade procedure|
| POOL_RESTART     |`action`|`*`|`*`|TRUSTEE| Restarting pool command|
| POOL_CONFIG      |`action`|`*`|`*`|TRUSTEE| Pool config command (like a `read only` option)| 
| VALIDATOR_INFO   |`*`|`*`|`*`| TRUSTEE, STEWARD, NETWORK_MONITOR| Getting validator_info from pool|


### Also, there is a some optional rules for case if in config option ANYONE_CAN_WRITE is set to True:
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
|NYM               |`role`|`<empty>`|`<empty>`| Anyone| Adding new nym|
|SCHEMA            |`*`|`*`|`*`| Anyone| Any operations with SCHEMA transaction|
|CLAIM_DEF         |`*`|`*`|`*`| Anyone| Any operations with CLAIM_DEF transaction|


### As of now it's not implemented yet, but the next rules for Revocation feature are needed:
#### If ANYONE_CAN_WRITE is set to False:
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
|REVOC_REG_DEF|`*`|`*`|`*`| TRUSTEE, STEWARD, TRUST_ANCHOR| Adding new REVOC_REG_DEF|
|REVOC_REG_DEF|`*`|`*`|`*`| Only owners can edit existing REVOC_REG_DEF| Editing REVOC_REG_DEF|
|REVOC_REG_ENTRY|`*`|`*`|`*`| Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY| Adding new REVOC_REG_ENTRY|
|REVOC_REG_ENTRY|`*`|`*`|`*`| Only owners can edit existing REVOC_REG_ENTRY| Editing REVOC_REG_ENTRY|

#### If ANYONE_CAN_WRITE is set to True:
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
|REVOC_REG_DEF|`*`|`*`|`*`| Anyone can create new REVOC_REG_DEF| Adding new REVOC_REG_DEF|
|REVOC_REG_DEF|`*`|`*`|`*`| Only owners can edit existing REVOC_REG_DEF| Editing REVOC_REG_DEF|
|REVOC_REG_ENTRY|`*`|`*`|`*`| Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY| Adding new REVOC_REG_ENTRY|
|REVOC_REG_ENTRY|`*`|`*`|`*`| Only owners can edit existing REVOC_REG_ENTRY| Adding new REVOC_REG_ENTRY|
