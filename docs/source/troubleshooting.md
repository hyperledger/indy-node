
# Indy Node troubleshooting guide

## Background info

From deployment point of view Indy Node is highly available replicated database, capable of withstanding crashes and malicious behavior of individual **validator** nodes, collectively called **pool**.
In order to do so Indy Node uses protocol called RBFT, which is leader-based byzantine fault tolerant protocol for **ordering** transactions - agreeing upon global order between them on all non-faulty nodes, so that nodes will always write them in same order into their **ledgers** (which are basically transaction logs with merkle tree on top, so that consistency can be easily checked) and end up in same **state** (which is a key-value storage based on Merkle Patricia Tree) after executing ordered transactions.
This protocol guarantees both safety and liveness as long as no more than **f=N/3** nodes (rounding down) are faulty (either unavailable or performing malicious actions), where **N** is number of all validator nodes.

Protocol progresses (in other words - performs writes) as long as leader node (called **master primary**) creates new **batches** (sets of transactions to be executed), which are then agreed upon by at least of **N-f** of nodes, including master primary.
Performance of pool is capped by performance of current master primary node - if it doesn't propose new batches then there is nothing to agree upon and execute by the rest of the pool.
If master primary for some reason is down, or tries to perform some malicios actions (including trying to slow down writes) pool elects a new leader using subprotocol called **view change**.
Note that during view change incoming write requests are rejected, however read requests are normally processed.

In order to catch performance problems RBFT actually employs _f+1_ PBFT protocol instances, one of them called master, and other backups, each with its own leader node, called primary (so master primary is just a leader of master instance, and leaders of other instances are called **backup primaries**).
Each instance works independently and spans all nodes (meaning all nodes run all instances), but only transactions ordered by master instance are actually executed.
Sole purpose of backup instances is to compare their performance to master instance and initiate a view change if master primary is too slow.
Instances are numbered, master is always 0, and backups are assigned numbers starting from 1.

When node is starting up or detects that it is lagging behind the rest of the pool it can start process of **catch up**, which is basically downloading (along with consistency checks) of latest parts of ledgers from other nodes and applying transactions to state.
More info about internals of Indy Node, including sequence diagrams of different processes can be found [here](https://github.com/hyperledger/indy-plenum/tree/master/docs/source/diagrams).

In order to be capable of automatically [upgrading](https://github.com/hyperledger/indy-node/blob/master/docs/source/pool-upgrade.md) itself Indy Node employs separate service called `indy-node-control`, which runs along with main service called `indy-node`.
Also it is worth noting that `indy-node` service is configured to automatically restart node process in case it crashes.

### Types of failures

In an ideal world network connections are always stable, nodes do not fail, and software doesn't have bugs. 
Unfortunatelly in real world this is not the case, so Indy Node pool can fail in some circumstances.

Most of failures can divided into following categories (in order of increasing severity):
- failures induced by environment problems, like misconfigured firewalls preventing nodes connecting to each others
- transient consensus failures on some nodes, most likely to some unhandled edge cases, which can go away after restarting affected nodes
- node failures, like inability to properly perform an upgrade or handle some incoming request due to some bug, which require manual intervention, but doesn't affect ledger data
- ledger corruption, which require touching ledger data in order to fix it

Of course, if number of affected nodes is _f_ or less then from external point of view functionality of pool will be unaffected.
However if more than _f_ nodes become affected then pool will not be able to do writes, although pool still will be able to process reads until all nodes fail.

### Where to get info

Most useful places get info are the following:
- [Indy CLI](https://github.com/hyperledger/indy-sdk/tree/master/cli) can be used for sending read and write requests to pool, as well as checking general connectivity.
- Either VALIDATOR_INFO command sent through Indy CLI (in case of Sovrin network you'll need to have keys for priveleged DID to do so), or [validator-info](https://github.com/hyperledger/indy-node/blob/master/design/validator_info.md) script run on validator node.
  These tools provide important information like how many nodes are connected to each other, when last write happened (due to freshness check it should happen at least once per 5 minutes), whether a view change is in progress now or other important data, which is useful to assess pool current health and can be a starting point for further investigation, when needed.
- `journalctl` logs can be useful because they contain tracebacks of indy-node crashes, if they happened, and these logs are really easy to check.
  Sometime crashes can be due to some bugs in code, but also they can be caused by insufficient resource (either memory or disk space), and if this is the case `journalctl` logs can provide a quick answer.
- Indy node logs, located in `/var/log/indy/<network name>/`.
  They can provide a lot of historical information, and very often are enough to get enough clues in order to properly diagnose situation, however they can be hard to read for unprepared.
  Lately most of the time it was enough to use `grep` and `sort` command-line tools to analyze them (although we'd recommend using [ripgrep](https://github.com/BurntSushi/ripgrep/releases) instead of plain grep, as it has quite a bunch of usability and performance improvements over traditional grep, while having compatible interface and no extra dependencies).
  However we also have a [process_logs](https://github.com/hyperledger/indy-plenum/tree/master/scripts/process_logs) utility script, which also can be useful.
  More info about them will be provided in next sections.
- Indy node control tool logs, located in `/var/log/indy/node_control.log`.
  They can be useful when investigating upgrade-related problems.
- In case of Sovrin network there are public websites showing contents of different ledgers, even if network is down (they basically mirror ledgers in their local database).
  We find most user-friendly one to be [indyscan.io](https://indyscan.io).
  This can be useful as a quick check whether some transaction type was written in the past when investigating transaction-specific problems.
- When in doubt about connectivity issues due to misconfigured firewalls or DPI a purpose-build tool [test_zmq](https://github.com/hyperledger/indy-plenum/blob/master/scripts/test_zmq/README.md) can be used.
- Debug metrics.
  They are turned off by default, but can be turned on by adding `METRICS_COLLECTOR_TYPE = 'kv'` to `/etc/indy/indy_config.py` and restarting node.
  Tools for processing these metrics are scripts `process_logs` and `build_graph_from_csv` bundled with Indy Node.
  Debug metrics can be used to find some insidios problems like memory leaks and some other hard to detect problems.

### Node data structure

Node stores all data (except local configuration and logs) in `/var/lib/indy/<network name>`.
Among other things it contains following data:
- `keys` subdirectory contains node keys, including private ones.
  **Never ever share this folder with 3rd party!**
- `data` contains various databases, including ledgers, states and various caches.
  Since all data inside this directory is effectively public it should be safe to share its contents, for example for debugging purposes.

Directory `/var/lib/indy/<network name>/data/<node_name>` contains directories with RocksDB databases, most interesting ones are:
- `*_transactions` contains transaction data of ledgers (`*` here can be `audit`, `domain`, `config`, `pool` and possibly some plugin ledgers)
- `*_merkleNodes` and `*_merkeLeaves` contain merkle trees for transaction data of ledgers.
  This data can be rebuilt from transactions data if needed.
- `*_state` contains state in a form of merkle patricia tree (note that there is no state for `audit` ledger, only for `domain`, `config`, `pool` and possibly some plugin ledgers).
  This data can be rebuilt from transactions data if needed, however if after such rebuild root hashes change clients won't be able to get state proofs in order to trust replies from any single node and will fallback to asking `f+1` nodes for such hashes.
  This shouldn't be a problem with queries on current data since it gets updated with every new batch ordered (including empty freshness batches), but it can degrade performance of accessing some historical data.

## Troubleshooting checklist

### Emergency checklist

In case of client-visible incidents first of all assess how bad situation is and try to fix it as soon as possible:
- If failure happened after upgrade
  - Check that upgrade successfully finished, and all nodes have same versions, if not - investigate and fix it first
- If it is impossible to read from ledger
  - Check whether problem affects all read transactions, or just some subset of them.
    Latter case indicates that most probably there is a bug in source code.
    This needs longer investigation, but on the other hand it doesn't affect all use cases.
    First place to look at should be journalctl to make sure nodes are not crashing on receiving transactions.
  - If problem affects all read transactions:
    - Check whether nodes are accessible at all from client (using tools like `netcat`).
      Nodes IPs and ports can be found in pool ledger, which should be present on client.
      In case of Sovrin network nodes addresses also could be found from some 3rd party sites like [indyscan.io](https://indyscan.io).
    - If nodes are inaccessible from client check whether nodes are actually running and firewalls are configured properly (by asking corresponding Stewards).
      When coordinating with Stewards an additional [purpose-built tool](https://github.com/hyperledger/indy-plenum/blob/master/scripts/test_zmq/README.md) can be used for checking ZeroMQ connectivity.
    - If nodes are running, but do not respond - check journalctl logs, there is a high change that nodes are perpetually crashing while trying to start up.
      This needs investigation (but usually it shouldn't take too long, since stack trace is available) and fixing source code.
- If it is implossible to write to ledger
  - Check whether problem affects all write transactions, or just some subset of them.
    Latter case indicates that most probably there is a bug in source code.
    This needs longer investigation, but on the other hand it doesn't affect all use cases.
    First place to look at should be journalctl to make sure nodes are not crashing on receiving transactions.
  - If problem affects all write transactions (meaning that write consensus is lost):
    - Check whether there is an ongoing view change (write requests are rejected during view change), if so - it could be reasonable to give it some time to finish.
    If it doesn't finish in 5 minutes proceed to next checks.
    - Check whether at least _N-f_ nodes are online, if not - start more nodes.
    - Check that all online nodes (and especially master primary) are connected to each other, if not - most probably it is firewall issues which need to be fixed.
    - Check that all started nodes are participating in consensus (i.e. not in catch-up or view change state)
      - if some are stuck in catch up or view change - try rebooting them individually, this could help if error condition is transient
      - if majority of nodes are stuck - send POOL_RESTART action to simultaneosly restart whole pool, this could help if error condition is transient
      - if restart doesn't help (and it is not a ledger or state corruption, see below) problem needs deeper investigation
    - Check all nodes have same state - if some nodes appear to be corrupted (in this case corrupted nodes usually contain `incorrect state trie` messages in their logs) delete state from them and restart, they should be able to recreate correct state from ledger, unless there is some bug in code or ledger itself is corrupted.
    - Check all nodes have same ledgers - if some nodes appear to be corrupted (their logs can contain `incorrect state trie`, `incorrect audit root hash`, `blacklisting` etc) it makes sense to delete all data from them and let them catch up from healty nodes. **This should be done with extreme care, and only if number of corrupted nodes is minor (certainly less than _f_).** Also, after deleting corrupted ledgers it is advised to check whether offending nodes were blacklisted by others, and if so - restart nodes that performed blacklisting.

### Recommended regular health checks

Indy Node pool can function even with some nodes failing, however it is better to catch and fix these failures before too many nodes are affected and we end up with major incident. First things to look at are:
- check that there are no crashes in journalctl, if there are some - investigate reasons, if it leads to finding some bugs - fix them
- check that all nodes can connect to each other, if not - it is most likely firewall issue which needs to be fixed
- check that all nodes participate in consensus, and are not stuck in view change or catch up, if not - investigate why they became stuck and reboot them
- check that all nodes have correct ledgers and state, if not - investigate why it diverged and then fix (usually by deleting state or full data and letting node restore it)
- check that nodes are not blacklisting each other, if they do some blacklisting - investigate and fix offending node and then restart all nodes that blacklisted it

**Warning:** when significant number of nodes is out of consensus try to refrain from sending promotion/demotion transactions, especially many in a row.

### First things to look at in node logs during investigations

- `incorrect <anything except time>` - if you see in logs messages blaming some PREPREPAREs to have `incorrect state trie`, `incorrect audit root hash` or the like it means that we've got data corruption.
  If this happened next steps would be:
  - try to understand how many and which nodes got their data corrupted:
    - if these messages are seen on minority of nodes, and view change doesn't happen, then it is these nodes have data corrupted
    - if these messages are seen on majority of nodes, but then view change happens and ordering continues normally, then data corruption happened on primary and non-blaming nodes (after view change they should start blaming new primary for incorrect PREPREPAREs, since view change will reduce situation to previous case)
  - try to understand what exactly is corrupted and why:
    - look through `journalctl` logs for recent crashes, especially due to memory or disk space errors. 
      Sometimes crashes can lead to data corruption.
    - look through node logs for recent view changes - this is quite a complex process, which sometimes led to data corruption in the past (now this is hopefully fixed with correct implementation of PBFT view change)
    - if warning was on `incorrect state trie` then most likely only state was corrupted.
      In this case you can try to stop node, delete state and start it again - node should be able to rebuild correct state from transactions log (ledger).
      If deleting state doesn't help, and node continues complaining on incorrect state trie, then situation is worse, and probably there is a bug

- `incorrect time` - if you see in logs messages blaming some PREPREPAREs to have `incorrect time`, then there is either one of the following:
  - either primary node, or node complianing on `incorrect time` has local clock set significantly off, if this is the case clock needs to be adjusted
  - incoming message queues are filled up faster than processed - which can be indirectly confirmed by increased memory consumption.
    Possible reasons behind this might be:
    - previous PREPREPARE messages were also discarded, but by some other reason.
      If this is the case having PREPREPAREs with incorrect time is just a consequence
    - there was some performance spike, which caused at first some message delays, followed by an avalanche on message requests.
      This can be fixed by pool restart (using POOL_RESTART transaction)
    - there is too much load on the pool (very unlikely situation for current Sovrin deployments, but we've seen this during load tests against test pools)

- `blacklisting` - this message can be seen during catchup when some node find that some other node tries to send it transactions which are not in ledgers of other nodes.
  Usually this indicates that ledger corruption happened somewhere, which can be diagnosed and fixed like described above in "incorrect state/audit" section.
  There is twist however - even if offending node is fixed other nodes retain their blacklists until restart.

### Useful fields in validator info output

- `Software` - this can be useful for checking what exact versions of indy-related packages are installed
- `Pool_info` - shows generic pool parameters and connectivity status, most useful fields are:
  - `Total_nodes_count` - number of validator nodes in pool
  - `f_value` - maximum number of faulty nodes that can be tolerated without affecting consensus, should be `Total_nodes_count/3` rounded down
  - `Unreachable_nodes_count` - number of nodes that cannot be reached, ideally should be 0, if more than `f_value` write consensus is impossible
  - `Unreachable_nodes` - list of unreachable nodes, ideally should be empty
  - `Blacklisted_nodes` - list of blacklisted nodes, should be empty, if not and blacklisted nodes were already fixed blacklisting node should be rebooted to clear this list
- `Node_info` - shows information about node
  - `Mode` - operation mode of node, normally it should be `participating`, if not - node is not participating in write consensus
  - `Freshness_status` - status of freshness checks (periodic attempts to order some batch on master instance) per ledger, usually either all are successfull, or all are failed. Latter case means that at least on this node write consensus is broken. If write consensus is broken on more than _f_ nodes then it is certainly broken on all nodes, meaning pool has lost write consensus and cannot process write transactions.
  - `Catchup_status` - status of either last completed or currently ongoing catchup
    - `Ledger_statuses` - catchup statuses of individaul ledgers, if some are not `synced` then it means that there is an ongoing catchup
  - `View_change_status` - status of either last completed or currently ongoing view change
    - `View_No` - current view no, should be same on all nodes.
    If there is an ongoing view change this will indicate target view no.
    - `VC_in_progress` - indicates that there is an ongoing view change at least on this node, this shouldn't last for more than 5 minutes (actually in most cases view change should complete in under 1 minute).
    Usually all nodes should start and finish view change approximately at the same time, but sometimes due to some edge cases less than _f_ nodes can enter (or fail to finish) view change and linger in this state indefinitely.
    In this case it is advised to try to reboot such nodes, and if doesn't help - investigate situation further.
    - `Last_complete_view_no` - indicates view no of last completed view change
    - `IC_queue` - list of received instance change messages (effectively votes for view change) which didn't trigger a view change yet (at least _N-f_ votes for view change to same view_no is needed)


### Useful patterns in logs

- `Starting up indy-node` - node just started. This can be useful to identify restart points among other events
- `starting catchup (is_initial=<>)` - node started catching up
- `transitioning from <state> to <state>` - node successfully progressed through catch up. If node fails to finish catch up this could help identify exact stage which failed
- `caught up to <n> txns in last catch up` - node successfully finished a catch up
- `sending an instance change` - this shows our node voted for a view change (and includes reason for doing so)
- `received instance change request` - this indicates that we received vote for a view change from some other node. When node gets _N-f_ instance change messages (including ours) with same `view_no` (however `code` can be different) it starts a view change. This message also can be very useful when you have access to logs from a limited number of nodes but need to diagnose problems happening on other nodes. Codes which are most likely to occur:
  - 25 - master primary has too low performance
  - 26 - master primary disconnected (which means it cannot propose new batches to order, and pool needs to select a new one)
  - 28 - there is an ongoing view change, and it failed to complete in time
  - 43 - too much time has passed since last successfully ordered batch (in other words node suspects that pool cannot perform write transactions anymore)
  - 18 - time of PREPREPARE received from master primary is way too off, this can also indirectly indicate that incoming message queues are filled faster than processed
  - 21 - state trie root hash of received PREPREPARE looks incorrect, **this indicates ledger corruption**, refer to [this](#first-things-to-look-at-in-node-logs-during-investigations) section for more details
  - 44 - audit root hash of received PREPREPARE looks incorrect, **this indicates ledger corruption**, refer to [this](#first-things-to-look-at-in-node-logs-during-investigations) section for more details
  - 46-51 - these codes are connected to promotions or demotions of validator nodes, and:
    - either indicate that some nodes were promoted or demoted, in which case pool need to choose a new primary, hence votes for view change
    - or indicate some transient problems when selecting new primary after changing number of nodes, so yet another view change is needed
  - other suspicion codes can be found [here](https://github.com/hyperledger/indy-plenum/blob/master/plenum/server/suspicion_codes.py)
- `started view change to view` - this marks start of view change
- `finished view change to view` - view change service accepted NEW_VIEW message (so there is enough connectivity between honest nodes to reach consensus), however there are some cases when ordering in new view fails and another view change will be needed
- `started participating` - node finished all side activities (like catch up or view change) and started participating in consensus
- `0 ordered batch request` - node master instance just managed to order one more batch of transactions (so there is write consensus)
- `<n> ordered batch request` - some backup instance just managed to order one more batch (so there is write consensus on backups, but that doesn't mean write consensus on master, which matters for clients).
- `disconnected from <node>` - for some reason we lost connection to some other validator node
- `now connected to <node>` - we managed to connect to some other validator node after being disconnected
- `connections changed from <list> to <list>` - duplicates information about connection and disconnection events, it can be useful for quickly checking list of connected nodes at given point in time without needing to track all previous individual connection events. Previous data can 
