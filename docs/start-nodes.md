# Create a Network and Start Nodes

In order to run your own Network, you need to do the following for each Node:
1. Install Indy Node
    - A recommended way for ubuntu is installing from deb packages
    ```
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
    sudo echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list
    sudo apt-get update
    sudo apt-get install indy-node
    ```
    - It's also possible to install from pypi for test purposes
        - master version: `pip install indy-node-dev`
        - stable version: `pip install indy-node`
2. Initialize Node to be included into the Network
    - if ```indy-node``` were installed from pypi basic directory structure should created manually with the command ```create_dirs.sh```
    - set Network name in config file
        - the location of the config depends on how a Node was installed. It's usually inside `/etc/indy` for Ubuntu.
        - the following needs to be added: `NETWORK_NAME={network_name}` where {network_name} matches the one in genesis transaction files above
    - generate keys
        - ed25519 transport keys (used by ZMQ for Node-to-Node and Node-to-Client communication)
        - BLS keys for BLS multi-signature and state proofs support
    - provide genesis transactions files which will be a basis of initial Pool.
        - pool transactions genesis file:
            - The file must be named as `pool_transactions_genesis`
            - The file contains initial set of Nodes a Pool is started from (initial set of NODE transactions in the Ledger)
            - New Nodes will be added by sending new NODE txn to be written into the Ledger
            - All new Nodes and Clients will use genesis transaction file to connect to initial set of Nodes,
            and then catch-up all other NODE transactions to get up-to-date Ledger.
            - File must be located in ```/var/lib/indy/{network_name}``` folder
        - domain transactions genesis file:
            - The file must be named as `domain_transactions_genesis`
            - The file contains initial NYM transactions (for example, Trustees, Stewards, etc.)
            - File must be located in ```/var/lib/indy/{network_name}``` folder
    - configure iptables to limit the number of simultaneous clients connections (recommended)

## Scripts for Initialization

There are a number of scripts which can help in generation of keys and running a test network.

#### Generating keys

###### For deb installation
The following script should be used to generate both ed25519 and BLS keys for a node named `Alpha` with node port `9701` and client port `9702`
```
init_indy_node Alpha 9701 9702 [--seed 111111111111111111111111111Alpha]
```
Also this script generates indy-node environment file needed for systemd service config and indy-node iptables setup script.

###### For pip installation
The following script can generate both ed25519 and BLS keys for a node named `Alpha`
```
init_indy_keys --name Alpha [--seed 111111111111111111111111111Alpha] [--force]
```

Note: Seed can be any randomly chosen 32 byte value. It does not have to be in the format 11..<name of the node>

Please note that these scripts must be called *after* CURRENT_NETWORK is set in config (see above).


#### Generating keys and test genesis transaction files for a test network

There is a script that can generate keys and corresponding test genesis files to be used with a Test network.

```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 [--ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'] [--network=sandbox]
```
- `--nodes` specifies a total number of nodes in the pool
- `--clients` specifies a number of pre-configured clients in the pool (in `domain_transactions_file_{network_name}_genesis`)
- `--nodeNum` specifies a number of this particular node (from 1 to `-nodes` value), that is a number of the Node to create private keys locally for.
- `--ip` specifies IP addresses for all nodes in the pool (if not specified, then `localhost` is used) 
- `--network` specifies a Network generate transaction files and keys for. `sandbox` is used by default.
 
We can run the script multiple times for different networks. 

#### Setup iptables (recommended)

###### For deb installation
To setup the limit of the number of simultaneous clients connections it is enough to run the following script without parameters
```
setup_indy_node_iptables
```
This script gets client port and recommended connections limit from the indy-node environment file.

NOTE: this script should be called *after* `init_indy_node` script.

###### For pip installation
The `setup_indy_node_iptables` script can not be used in case of pip installation as indy-node environment file does not exist,
use the `setup_iptables` script instead (9702 is a client port, 15360 is recommended limit for now)
```
setup_iptables 9702 15360
```
In fact, the `setup_indy_node_iptables` script is just a wrapper for the `setup_iptables` script.

NOTE: you should be a root to operate with iptables.

#### Running Node

The following script will start a Node process which can communicate with other Nodes and Clients
```
start_indy_node Alpha 9701 9702
```
The node uses separate TCP channels for communicating with nodes and clients.
The first port number is for the node-to-node communication channel and the second is for node-to-client communication channel.

## Local Test Network Example 


If you want to try out an Indy cluster of 4 nodes with the nodes running on your local machine, then you can do the following:

```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 2 3 4
By default node with the name Node1 will use ports 9701 and 9702 for nodestack and clientstack respectively
Node2 will use ports 9703 and 9704 for nodestack and clientstack respectively
Node3 will use ports 9705 and 9706 for nodestack and clientstack respectively
Node4 will use ports 9707 and 9708 for nodestack and clientstack respectively
```

Now you can run the 4 nodes as
```
start_indy_node Node1 9701 9702
```
```
start_indy_node Node2 9703 9704
```
```
start_indy_node Node3 9705 9706
```
```
start_indy_node Node4 9707 9708
```

## Remote Test Network Example 

Now lets say you want to run 4 nodes on 4 different machines as
1. Node1 running on 191.177.76.26
2. Node2 running on 22.185.194.102
3. Node3 running on 247.81.153.79
4. Node4 running on 93.125.199.45

For this
On machine with IP 191.177.76.26 you will run
```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node1 will use ports 9701 and 9702 for nodestack and clientstack respectively
```

On machine with IP 22.185.194.102 you will run
```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 2 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node2 will use ports 9703 and 9704 for nodestack and clientstack respectively
```

On machine with IP 247.81.153.79 you will run
```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 3 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node3 will use ports 9705 and 9706 for nodestack and clientstack respectively
```

On machine with IP 93.125.199.45 you will run
```
~$ generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 4 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node4 will use ports 9707 and 9708 for nodestack and clientstack respectively
```

Now you can run the 4 nodes as
```
start_indy_node Node1 9701 9702
```
```
start_indy_node Node2 9703 9704
```
```
start_indy_node Node3 9705 9706
```
```
start_indy_node Node4 9707 9708
```