# Extension of validator_info
The document contains list of possible extensions and modifications of validator_info command to simplify node state monitoring and debug process

* [Validator_info Description](#cur-description)
* [Modification - New Read Command](#new-command)
* [Extension - Additional Fields](#new-fields)

## Validator_info Description
Validator_info is a script that formats and prints data provided by node. The script should be run manually by
the user who has a read access to the \<node name\>_info.json file from the node's data directory.
This file is updated by node once a minute and contains following information:
```
{
    "did": "Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv", # node's identidier
    "response-version": "0.0.1", # 0.0.1 for now
    "timestamp": 1519711338, # current time 
    "verkey": "33nHHYKnqmtGAVfZZGoP8hpeExeH45Fo8cKmd5mcnKYk7XgWNBxkkKJ", # node's verkey
    "pool": { # current pool
        "reachable": { # reachable nodes
            "list": ["Node1", "Node2", "Node3", "Node4"],
            "count": 4
         },
        
        "total-count": 4, # total count of nodes
        "unreachable": { # unreachable nodes
           "list": [],
           "count": 0
        }
     },
    
    "bindings": { # node's network configuration
       "client": {
            "port": 9702,
            "protocol": "tcp"
        },
       
       "node": {
            "port": 9701,
            "protocol": "tcp"
        }
    },
    
    "metrics": { # some numeric characteristics
        "transaction-count": { # txn count by ledger
            "pool": 4,
            "ledger": 19,
            "config": 0
        },
        
        "average-per-second": { # performance counters
            "write-transactions": 0.013294133790137249,
            "read-transactions": 0.0
        },
        
        "uptime": 300 # uptaime
    },
    
    "software": { # packets' versions
        "indy-node": "1.3.319",
        "sovrin": null
    },
    
    "alias": "Node1" # node's name
}
```

## Modification - New Read Command
Validator_info accessible as read command, available for Steward and Trustee. New command VALIDATOR_INFO provide info from
all the connected nodes without need of consensus (similar to force=True flag in upgrade cmd).
Command allow requesting all parameters or some subset of parameters.

The client sends a command with some parameters to each node. There are only one parameter now - node alias for get its info. But parameters list will expanded later.
After receiving the request, each node get data from its field, and then sends the Json result without compression to the client.
The client should not wait for the consensus of the all node, but should handle the response from each node separately.

For reference: [INDY-1184](https://jira.hyperledger.org/browse/INDY-1184)


## Extension - Additional Fields

* Host machine info
    * Hardware
        * HDD free space
        * RAM available
        * MBs used by node process
        * Node's data folder size
    * Software
        * OS version
        * pip freeze output
        * all indy related packets versions
    * Current datetime and timezone

* Configuration
    * Config
        * Content of main config
        * Content of network config
        * Content of user config
    * Content of Genesis Transaction Files
    * indy.env
    * node_control.conf
    * indy-node.service
    * indy-node-control.service
    * iptables related config
    
* Extraction from logs and ledgers
    * grep exception from journalctl
    * grep view change, catch up, shutdown, instance change from the last log file
    * systemctl status indy-node
    * systemctl status indy-node-control
    * Uptime
    * upgrade_log
    * last N txns from pool ledger
    * last N txns from config ledger
    * last N txns from domain ledger
    * pool ledger size
    * config ledger size
    * domain ledger size 

* Pool info
    * Global pool settings
        * read-only mode
    * Nodes' connect/disconnect events for the last N min
    * Ping time to other nodes
    * Current quorum values
        * N value
        * f value
        * per action values
    * Reachable nodes
    * Unreachable nodes
    * Blacklisted nodes
    * List of Suspicious

* Protocol
    * supported client versions
    * supported protocol versions
    * supported requests versions

* Node info
    * name
    * last N txns from the pool ledger that belong to the current node only
    * current mode
    * metrics
    * view change status
        * instance_change msgs
        * waiting view_change_done msgs
    * catchup status
        * each ledger catchup status
        * last ledger_status msgs
        * waiting consistency_proof msgs
    * number of replicas
    * foreach replica
        * name
        * primary
        * root hashes
        * uncommitted txns count
        * uncommitted root hashes
        * watermarks
        * last_ordered
        * last_3pc key
        * info about stashed txns
            * total number of stashed txns
            * number of stashed checkpoints
            * min stashed PrePrepare
            * min stashed Prepare
            * min stashed Commit

For reference: [INDY-1175](https://jira.hyperledger.org/browse/INDY-1175)
