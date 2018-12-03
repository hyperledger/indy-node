# Current implemented rules in auth_map
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
| NYM              |`role` |`<empty>`       | TRUSTEE   | TRUSTEE|Adding new TRUSTEE|
| NYM              |`role` |`<empty>`       | STEWARD   | TRUSTEE|Adding new STEWARD|
| NYM              |`role` |`<empty>`       | TRUST_ANCHOR| TRUSTEE, STEWARD|Adding new TRUST_ANCHOR|
| NYM              |`role` |`<empty>`       |`<empty>`  | TRUSTEE, STEWARD, TRUST_ANCHOR| Adding new nym|
| NYM              |`role` | TRUSTEE        |`<empty>`  | TRUSTEE | Change role from TRUSTEE to None|
| NYM              |`role` | STEWARD        |`<empty>`  | TRUSTEE | Change role from STEWARD to None|
| NYM              |`role` | TRUST_ANCHOR   |`<empty>`  | TRUSTEE | Change role from TRUST_ANCHOR to None|
| NYM              |`verkey`|`*`|`*`| Owner of this nym | Any operations with verkey field|
| SCHEMA           |`*`|`*`|`*`| TRUSTEE, STEWARD, TRUST_ANCHOR | Any operations with SCHEMA transactions|
| CLAIM_DEF        |`*`|`*`|`*`| Owner of this claim_def txn| Any operations with CLAIM_DEF transaction|
| NODE             |`services`|`<empty>`|`[VALIDATOR]`| STEWARD if it is owner of this transaction| Add new node to pool|
| NODE             |`services`|`[VALIDATOR]`|`[]`| TRUSTEE, STEWARD if it is owner of this transaction| Demotion of node|
| NODE             |`services`|`[]`|`[VALIDATOR]`| TRUSTEE, STEWARD if it is owner of this transaction| Promotion of node|
| NODE             |`node_ip`|`*`|`*`| STEWARD if it is owner of this transaction| Change Node's ip address|
| NODE             |`node_port`|`*`|`*`| STEWARD if it is owner of this transaction| Change Node's port|
| NODE             |`client_ip`|`*`|`*`| STEWARD if it is owner of this transaction| Change Client's ip address| 
| NODE             |`client_port`|`*`|`*`| STEWARD if it is owner of this transaction| Change Client's port|
| NODE             |`blskey`|`*`|`*`| STEWARD if it is owner of this transaction| Change Node's blskey|
| POOL_UPGRADE     |`action`|`<empty>`|`start`|TRUSTEE| Start upgrade procedure|
| POOL_UPGRADE     |`action`|`start`|`cancel`|TRUSTEE| Cancel upgrade procedure|
| POOL_RESTART     |`action`|`*`|`*`|TRUSTEE| Restart pool command|
| POOL_CONFIG      |`action`|`*`|`*`|TRUSTEE| Pool config command (like a `read only` option)| 
| VALIDATOR_INFO   |`*`|`*`|`*`| TRUSTEE, STEWARD| Get validator_info from pool|

### Also, there is a some optional rules for case if in config option ANYONE_CAN_WRITE is set to True:
| Transaction type | Field | Previous value | New value | Who can| Description |
|------------------|-------|----------------|-----------|--------|-------------|
|NYM               |`role`|`<empty>`|`<empty>`| Anyone| Adding new nym|
|SCHEMA            |`*`|`*`|`*`| Anyone| Any operations with SCHEMA transaction|
|CLAIM_DEF         |`*`|`*`|`*`| Anyone| Any operations with CLAIM_DEF transaction|
