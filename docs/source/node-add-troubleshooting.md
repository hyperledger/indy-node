# Troubleshooting - Adding or Upgrading Indy Nodes
Things can go wrong while adding or upgrading nodes on an existing Indy network and this guide will cover symptoms and issues encountered and some steps you might take to recover from those. The steps listed are likely just possible remedies to the listed issues. Feel free to add more remedies or issues if you don't see your's included here. As bugs are fixed, the issues noted below might not occur any more, or might have a different remedy.

## Adding a Node
This section covers troubleshooting the addition of a node to a network.  This can occur either as part of an upgrade (e.g. the 20.04 upgrade) or as part of a new node being added to an existing network.

### Symptom 1 - Node is unresponsive  
- Cause #1 - Node is performing catchup. (Large Network)
If your node appears unresponsive after adding it to a network (i.e. validator-info shows non-incrementing subledger counts) and no other symptoms are evident, then the first thing to do is wait. While smaller networks with a low number of transactions seem to perform "catchup" quite fast (within a minute or two for a domain ledger with 15K transactions) larger networks or networks that have been running for a long time can take 3 hours or more. Networks do not respond or recover well if you restart a node while it is performing catchup, so please be patient. To verify that this is the cause first check that the node is connected to the Primary Node (if not, see Cause #2), then check the logs to verify that normal "catchup" operations are in process. The best remedy for this would be to apply the "Best Practice" listed in the Validator Preparation Guide which suggests to "pre-fill" the data directory, especially on large networks, before starting a node for the first time. 
- Cause #2 - Node is not connected to the Primary Node 
If the added node cannot reach the primary node, then it sometimes has problems with catchup. Further symptoms in this case include Out Of Consensus (OOC) for your node and possibly others. 
If you realize the issue quickly, you might be able to recover from this by simply a) stopping the node, b) repairing the connection and then c) restarting the node. Otherwise, to recover you will need to perform the following:
1.    Stop indy-node on the new node
         `sudo systemctl stop indy-node`
1.    Remove the new node from the network using the indy-cli (if the network is OOC, see instructions below for restoring consensus, then return here and try again)
         `ledger node target=<new nodes id> alias=<alias> services=` 
1.    Repair the connection issue from the new node to the Primary Node (e.g. fix the new node or the primary nodes firewall?)
1.    After connection to the primary is verified, remove the "data" directory on the new node. The data directory will be recreated when the node starts back up.  This step clears out any possible corruption that might have occurred while the new node was unable to connect to the Primary node.
         `sudo rm -rf /var/lib/indy/<network_name>/data`
1.    Add the node back to the ledger with VALIDATOR privileges (indy-cli)
         `ledger node target=<new nodes id> alias=<alias> services=VALIDATOR`
1.    Start indy-node on the new node
         `sudo systemctl start indy-node`
### Symptom #2 - General Network Connectivity
Sometimes network connectivity issues have unexpected consequences and manifestations. Here is a checklist of items that might help correct for some of the odd cases that have been seen:
1. Firewall - Double check that both of the ports are open only for the matching interfaces and that all of the Node ports' allowed-list items have the correct port and IP's associated with them. Also check (where applicable) that you have assigned the correct security group and that each interface only has it's own security group assigned to it.  Also check that the Client IP and interface are "allowed" for the world and that the Node IP and interface are restricted to only allow other nodes on your network. 
1. On the node, run `ip a` and note the internal (local) ip addresses of your Client and Node interfaces. Then run `cat /etc/indy/indy.env` and verify that the internal ip addresses are used in the appropriate places. For at least AWS/GCP/Azure nodes, it's important not to have "0.0.0.0" used as the ip addresses in the files, as it causes weird connection problems that are difficult to diagnose.
1. More?

### Symptom #3 - Out of Consensus (OOC)
OOC can happen at any time and for a variety of reasons, not all of them known. Sometimes its just one node, and sometimes its several nodes all at once. Due to a presumed bug that has not yet been diagnosed or fixed, sometimes when adding a node to an existing network("large"?), the network goes OOC immediately. OOC is a serious state that does not allow writes to be made to the network and sometimes indicates a "slow response" even for reads, and thus should be dealt with at the first indication of even one node going OOC. Sometimes one node going OOC will lead to others following. If the network has entered a state where the nodes' primary node is not consistent (two or more primary nodes listed for the network nodes), then skip down to the "Multiple Primaries Symptom". Here's a general order of remedies to follow for returning the network to consensus:
- Restart the OOC nodes. 
1. From an Indy CLI:
 `ledger pool-restart action=start nodes=<comma separated list of nodes>`
1. or if all nodes are OOC:
 `ledger pool-restart action=start`
NOTE: This last command causes a brief but complete "Downtime" for the entire network and should only be run on "test networks" or as a last resort on production networks. While it is usually only down a few seconds, network "reads" will be incapable of occurring during that time. (Network "writes" are already not happening if the whole network is OOC.) That said, this complete restart regularly restores the network to an "in consensus" state.
- Remove the OOC node from participating in the network (then re-add).
Sometimes one node going OOC will lead to others having the same problem. If you can identify the node having or causing the problem (not always easy) removing it from the network then restarting the other nodes in the network (as mentioned immediately previously) can sometimes return the network to consensus. Then what? Sometimes adding the offending node back into the network immediately causes the problem to recur so the following steps are recommended:
1.    Stop indy-node on the offending node
         `sudo systemctl stop indy-node`
1.    Remove the new node from the network using the indy-cli 
         `ledger node target=<node id> alias=<alias> services=` 
1.    Remove the "data" directory on the offending node.
         `sudo rm -rf /var/lib/indy/<network_name>/data`
1.    (Optional) For larger networks this step might be required, but on smaller networks you can probably skip it. 
Get a full copy of the /var/lib/indy/<network_name>/data" directory from a "good" node and copy it to the offending node. Be sure to stop indy-node on the "good" node before zipping up a copy of the directory on it, then restart it when you are done. Yes, this could have some interesting side effects for an already troubled network...
1.    Add the node back to the ledger with VALIDATOR privileges (indy-cli)
         `ledger node target=<new nodes id> alias=<alias> services=VALIDATOR`
1.    Start indy-node on the offending node
         `sudo systemctl start indy-node`
NOTE: Sometimes when a node is added to a network and it exhibits poor behavior, as mentioned in several symptoms in this document, other nodes become "corrupted" in the process. In that case, performing the remedies in this symptom for each "corrupted node" may be required and is the recommended course of action.
### Symptom #4 Multiple Primaries
This is the case where different nodes on the network claim two or more nodes as the primary node (split-brain). This is likely caused by a "view change" bug that as yet is unresolved, but has occurred enough times to warrant a mention and steps for recovery here. This condition usually exists along with an OOC condition, but getting the primaries to agree should be the first step towards complete resolution (and sometimes also repairs the associated OOC condition). Our goal will be to get all nodes to re-agree to the primary that is the consistent one that most nodes agree on.
1. If the addition of a node to the network seems to have "caused" the multi-primary condition, remove that node from participating in the network. 
`ledger node target=<node id> alias=<alias> services=`
3. It is important to watch what is happening with the primary node changes on your network to determine what to do next. In the case of multiple primaries, regularly some of the nodes have a consistent primary that is the same, where the rest of the nodes are looping through a "view-change" process where their primary is changing somewhat rapidly. Watch the IndyMonitor tool and see which node are doing the rapid change and then make a list of those nodes. Add to that list any of the remaining nodes that have a different primary node than the majority.  In other words, find the nodes that seem to all have the same primary node that is unchanging then add all of the OTHER nodes to a list.
4. These next 2 steps must be done in relatively rapid succession, so make sure you are aware and prepared to do them before beginning. Run the following from the indy-cli using the list made in the previous steps.
`ledger pool-restart action=start nodes=<comma separated list of nodes>`
Wait for about 30 seconds, then run:
`ledger pool-restart action=start`
While this might seem a bit unusual, this two step "restart the network" has been the way that has worked to recover the network split-primary issues. If it doesn't work, try again and maybe wait a bit longer in between the two steps (the timing might be remembered incorrectly or might be somewhat arbitrary).
NOTE: Sometimes when a network begins to exhibit "split-brain" behaviours, in severe cases the symptoms will recur. A complete network reset may be required to remedy the issue if this happens on your network (or apply a future network upgrade that contains an undetermined fix).

#### Looking for other sypmtoms?
For issues not covered here, there's also a great guide with some deeper troubleshooting tips: [Indy Network Troubleshooting]( https://github.com/hyperledger/indy-node/blob/main/docs/source/troubleshooting.md)
