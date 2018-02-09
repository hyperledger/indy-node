# Pool Upgrade Guideline

There is quite interesting and automated process of the pool (network) upgrade.
- The whole pool (that is each node in the pool) can be upgraded automatically without any manual actions
via `POOL_UPGRADE` transaction. 
- As a result of Upgrade, each Node will be at the specified version,
 that is a new package, for example deb package, will be installed.
- Migration scripts can also be performed during Upgrade to deal with breaking changes between the versions. 


### Pool Upgrade Transaction

- Pool Upgrade is done via `POOL_UPGRADE` transaction.
- The txn defines a schedule of Upgrade (upgrade time) for each node in the pool.
- Only the `TRUSTEE` can send `POOL_UPGRADE`.
- This is a common transaction (written to config ledger), so consensus is required.
- There are two main modes for `POOL_UPGRADE`: forced and non-forced (default).
    - Non-forced mode schedules upgrade only after `POOL_UPGRADE` transaction is written to the ledger, that is 
there was consensus. Forced upgrade schedules upgrade for each node regardless of whether `POOL_UPGRADE` transaction is actually 
    written to the ledger, that is it can be scheduled even if the pool lost consensus.
    - Non-forced mode requires that upgrade of each node is done sequentially and not at the same time (so that
a pool is still working and can reach consensus during upgrade).
    Forced upgrade allows upgrade of the whole pool at the same time.
- One should usually use non-forced Upgrades assuming that all changes are backward-compatible.
- If there are non-backward-compatible (breaking) changes, then one needs to use forced Upgrade and 
make it happen at the same time on all nodes (see below).  
     
### Node Upgrade Transaction

- Each node sends `NODE_UPGRADE` transaction twice:
    - `in_progress` action: just before start of the Upgrade (that is re-starting the node and applying a new package)
    to log that Upgrade started on the node.
    - `success` or `fail` action: after upgrade of the node to log the upgrade result.
- `NODE_UPGRADE` transaction is a common transaction (written to config ledger), so consensus is required.

### Node Control Tool

- Upgrade is performed by a `node-control-tool`.
- See [`node_control_tool.py`](../indy_node/utils/node_control_tool.py).
- On Ubuntu it's installed as a systemd service (`indy-node-control`) in addition to 
the node service (`indy-node`).
- `indy-node-control` is executed from the `root` user.
- When upgrade time for the node comes, it sends a message to node-control-tool.
- The node-control-tool then does the following:
    - stops `indy-node` service;
    - upgrades `indy-node` package (`apt-get install` on Ubuntu);
    - back-ups node data (ledger, etc.);
    - runs migration scripts (see [`migration_tool.py`](../indy_node/utils/migration_tool.py));
    - starts `indy-node` service;
    - restarts `indy-node-control` service.
- If upgrade failed for some reasons, node-control-tool tries to restore the data (ledger) from back-up
 and revert to the version of the code before upgrade. 

### Migrations

- Although we must try keeping backward-compatibility between the versions, it may be possible
that there are some (for example, changes in ledger and state data format, re-branding, etc.).
- We can write migration scripts to support this kind of breaking changes and perform necessary steps
for data migration and/or running some scripts.
- The migration should go to `data/migration` folder under the package name (so this 
is `data/migration/deb` on Ubuntu).
- Please have a look at the following [doc](../data/migrations/README.md) for more information about how to write migration scripts.


### When to Run Forced Upgrades

- Any changes in Ledger transactions format leading to changes in transactions root hash.
- Any changes in State transactions format (for example new fields added to State values) requiring 
re-creation of the state from the ledger.
- Any changes in Requests/Replies/Messages without compatibility and versioning support.