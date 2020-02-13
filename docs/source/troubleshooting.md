
# Indy Node troubleshooting guide

## Background info

From deployment point of view Indy Node is highly available replicated database, capable of withstanding crashes and malicious behavior of individual **validator** nodes, collectively called **pool**.
In order to do so Indy Node uses protocol called RBFT, which is leader-based byzantine fault tolerant protocol for **ordering** transactions - agreeing upon global order between them on all non-faulty nodes, so that nodes will always end up in same **state** after executing ordered transactions.
This protocol guarantees both safety and liveness as long as no more than **f=N/3** nodes (rounding down) are faulty (either unavailable or performing malicious actions), where **N** is number of all validator nodes.
Protocol progresses (in other words - performs writes) as long as leader node (called **master primary**) creates new **batches** (sets of transactions to be executed), which are then agreed upon by at least of **N-f** of nodes, including master primary.
Performance of pool is capped by performance of current master primary node - if it doesn't propose new batches then there is nothing to agree upon and execute by the rest of the pool.
If master primary for some reason is down, or tries to perform some malicios actions (including trying to slow down writes) pool elects a new leader using subprotocol called **view change**.
In order to catch performance problems RBFT actually employs f+1 PBFT protocol instances, one of them called master, and other backups, each with its own leader node, called primary (so master primary is just a leader of master instance, and leaders of other instances are called **backup primaries**).
Each instance works independently and spans all nodes (meaning all nodes run all instances), but only transactions ordered by master instance are actually executed.
Sole purpose of backup instances is to compare their performance to master instance and initiate a view change if master primary is too slow.
Instances are numbered, master is always 0, and backups are assigned numbers starting from 1.

### Types of failures

In an ideal world network connections are always stable, nodes do not fail, and software doesn't have bugs. 
Unfortunatelly in real world this is not the case, so Indy Node pool can fail in some circumstances.

Most of failures can divided into following categories (in order of increasing severity):
- failures induced by environment problems, like misconfigured firewalls preventing nodes connecting to each others
- transient consensus failures on some nodes, most likely to some unhandled edge cases, which can go away after restarting affected nodes
- node failures, like inability to properly perform an upgrade or handle some incoming request due to some bug, which require manual intervention, but doesn't affect ledger data
- ledger corruption, which require touching ledger data in order to fix it

Of course, if number of affected nodes is f or less then from external point of view functionality of pool will be unaffected.
However if more than f nodes become affected then pool will not be able to do writes, although pool still will be able to process reads until all nodes fail.

### Where to get info

Most useful places get info are the following:
- either VALIDATOR_INFO command sent through Indy CLI, or `validator-info` script run on validator node. 
  These tools provide important information like how many nodes are connected to each other, when last write happened (due to freshness check it should happen at least once per 5 minutes), whether a view change is in progress now or other important data, which is useful to assess pool current health and can be a starting point for further investigation, when needed.
- `journalctl` logs can be useful because they contain tracebacks of indy-node crashes, if they happened, and these logs are really easy to check. 
  Sometime crashes can be due to some bugs in code, but also they can be caused by insufficient resource (either memory or disk space), and if this is the case `journalctl` logs can provide a quick answer.
- indy node logs, located in `/var/log/indy/<network name>/`. 
  They can provide a lot of historical information, and very often are enough to get enough clues in order to properly diagnose situation, however they can be hard to read for unprepared.
  Lately most of the time it was enough to use `grep` and `sort` command-line tools to analyze them (although we'd recommend using [ripgrep](https://github.com/BurntSushi/ripgrep/releases) instead of plain grep, as it has quite a bunch of usability and performance improvements over traditional grep, while having compatible interface and no extra dependencies).
  However we also have a [process_logs](https://github.com/hyperledger/indy-plenum/tree/master/scripts/process_logs) utility script, which also can be useful.
  More info about them will be provided in next sections.
- debug metrics. 
  They are turned off by default, but can be turned on by adding `METRICS_COLLECTOR_TYPE = 'kv'` to `/etc/indy/indy_config.py` and restarting node.
  Tools for processing these metrics are scripts `process_logs` and `build_graph_from_csv` bundled with Indy Node.
  Debug metrics can be used to find some insidios problems like memory leaks and some other hard to detect problems.

## Troubleshooting checklist

### First things to look at in logs

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
    - there is too much load on the pool (very unlikely situation for current Sovrin deployments, but we've seen this situation during load tests against test pools)

### Useful patterns in logs

- `Starting up indy-node` - node just started. This can be useful to identify restart points among other events
- `starting catchup (is_initial=<>)` - node started catching up
- `transitioning from <state> to <state>` - node successfully progressed through catch up. If node fails to finish catch up this could help identify exact stage which failed
- `caught up to <n> txns in last catch up` - node successfully finished a catch up
- `initiating a view change` - this marks start of view change
- `finished view change to view` - view change service accepted NEW_VIEW message (so there is enough connectivity between honest nodes to reach consensus), however there are some cases when ordering in new view fails and another view change will be needed
- `started participating` - node finished all side activities (like catch up or view change) and started participating in consensus
- `0 ordered batch request` - node master instance just managed to order one more batch of transactions (so there is write consensus)
- `<n> ordered batch request` - some backup instance just managed to order one more batch (so there is write consensus on backups, but that doesn't mean write consensus on master, which matters for clients).
