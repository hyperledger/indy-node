# Sovrin -- identity for all

Sovrin Identity Network public/permissioned distributed ledger

### Setup Instructions

#### Run common setup instructions
Follow instructions mentioned here [Common Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

### Run tests [Optional]

As sovrin-node tests needs sovrin-client which depends on Charm-Crypto, we need to install it.
Follow instructions mentioned here [Charm-Crypto Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

To run the tests, download the source by cloning this repo. 
Navigate to the root directory of the source and install required packages by

```
pip install -e .
```

Run test by 
```
python setup.py pytest
```

### Installing Sovrin node
Sovrin node can be installed using pip by
```
pip install -U --no-cache-dir sovrin-node
```

### Start Nodes

#### Initializing Keep
To run a node you need to generate its keys. The keys are stored on a disk in files in the location called `keep`. 
The  following generates keys for a node named `Alpha` in the keep. 
The keep for node `Alpha` is located at `~/.sovrin/Alpha`. 
```
init_sovrin_keys --name Alpha [--seed 111111111111111111111111111Alpha] [--force]
```


#### Running Node

```
start_sovrin_node Alpha 9701 9702
```
The node uses a separate UDP channels for communicating with nodes and clients. 
The first port number is for the node-to-node communication channel and the second is for node-to-client communication channel.


#### Running a Sovrin test cluster.
If you want to try out a Sovrin cluster of a few nodes with the nodes running on your local machine or different remote machines, 
then you can use the script called, `generate_sovrin_pool_transactions`. Eg. If you want to run 4 nodes on you local machine and have 
5 clients bootstrapped so they can make write requests to the nodes, this is what you do.

```
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 1
This node with name Node1 will use ports 9701 and 9702 for nodestack and clientstack respectively
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 2
This node with name Node2 will use ports 9703 and 9704 for nodestack and clientstack respectively
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 3
This node with name Node3 will use ports 9705 and 9706 for nodestack and clientstack respectively
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 4
his node with name Node4 will use ports 9707 and 9708 for nodestack and clientstack respectively
```

Now you can run the 4 nodes as 
```
start_sovrin_node Node1 9701 9702
```
```
start_sovrin_node Node2 9703 9704
```
```
start_sovrin_node Node3 9705 9706
```
```
start_sovrin_node Node4 9707 9708
```

These 4 commands created keys for 4 nodes `Node1`, `Node2`, `Node3` and `Node4`,
The `nodes` argument specifies the number of nodes and the `clients` argument specifies the number of client. 
The `nodeNum` argument specifies the node number for which you intend to create the private keys locally. 
Since you run on the machine where you run this command. Since you are running all 4 nodes on same machine you create private keys for all nodes locally.
 
Now lets say you want to run 4 nodes on 4 different machines as
1. Node1 running on 191.177.76.26
2. Node2 running on 22.185.194.102
3. Node3 running on 247.81.153.79
4. Node4 running on 93.125.199.45

For this
On machine with IP 191.177.76.26 you will run
```
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 1 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node1 will use ports 9701 and 9702 for nodestack and clientstack respectively
```

On machine with IP 22.185.194.102 you will run
```
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 2 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node2 will use ports 9703 and 9704 for nodestack and clientstack respectively
```

On machine with IP 247.81.153.79 you will run
```
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 3 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node3 will use ports 9705 and 9706 for nodestack and clientstack respectively
```

On machine with IP 93.125.199.45 you will run
```
~$ generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 4 --ips '191.177.76.26,22.185.194.102,247.81.153.79,93.125.199.45'
This node with name Node4 will use ports 9707 and 9708 for nodestack and clientstack respectively
```
