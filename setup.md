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

# Sovrin Client

Sovrin Client to interact with Sovrin Network (public/permissioned distributed ledger)

### Setup Instructions

#### Run common setup instructions
Follow instructions mentioned here [Common Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

Follow instructions mentioned here [Charm-Crypto Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

### Run tests [Optional]

Note: The tests create Sovrin nodes (dont worry, all nodes are created in the same process) . 

To run the tests, download the source by cloning this repo. 
Navigate to the root directory of the source and install required packages by
```
pip install -e .
```

Run test by 
```
python setup.py pytest
```


### Installing Sovrin client
```
pip install -U --no-cache-dir sovrin-client
```

Note. The tests create Sovrin nodes (dont worry, all nodes are created in the same process).

#### Configuration


### Start Sovrin client CLI (command line interface)
Once installed, you can play with the command-line interface by running Sovrin from a terminal.

Note: For Windows, we recommended using either [cmder](http://cmder.net/) or [conemu](https://conemu.github.io/).
```
sovrin
```



# Sovrin Common

Common utility functions for other Sovrin repos (like sovrin-client, sovrin-node etc)



### Charm-Crypto Setup Instructions

Sovrin-client requires anonymous credentials library which requires a cryptographic library.
The default configuration includes an example that uses Charm-Crypto framework.
The steps to install charm-crypto are mentioned in our [Anonymous Credentials](https://github.com/evernym/anoncreds) repository. 
You just have to run `setup-charm.sh` script. It will require sudo privileges on the system.


### Common Setup Instructions (sovrin-client or sovrin-node) 

As of Oct 3, these setup instructions are validated at a beta level.
We are aware of a few cases where you might hit roadblocks, depending
on what type of development environment you have. In particular, we
think you will have a bumpy ride on windows. We are working on improving
these instructions.

Developers should explore the [Getting Started Guide](getting-started.md) to learn how Sovrin works.

The Sovrin codebase makes extensive use of coroutines and the async/await keywords in
Python, and as such, requires Python version 3.5.0 or later. Plenum also
depends on libsodium, an awesome crypto library. These need to be installed
separately. Read below to see how.


#### Installing python 3.5 and libsodium:

**Ubuntu:**

Add a repository for python 3.5
```
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
```

Install python 3.5
```
sudo apt-get install python3.5
```

Install libsodium
```
sudo apt-get install libsodium13
```

If you get the error `E: Unable to locate package libsodium13` then add the following lines to your `/etc/apt/sources.list`

```
deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main
deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main
```

Now run
 
```
sudo apt-get update
sudo apt-get install libsodium13
```

While doing the above steps if you get the error

```
W: GPG error: http://ppa.launchpad.net trusty Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY B9316A7BC7917B12
```

Then you need to download the pubkey from the [OpenPGP Public Key Server](http://keyserver.ubuntu.com) and add it to your system. Steps to do that

1. Go to the [OpenPGP Public Key Server](http://keyserver.ubuntu.com)
2. Search for `0xB9316A7BC7917B12`
3. Click on the link provided in the pub section. This should take you to page containing the key.
4. Copy everything starting from `-----BEGIN PGP PUBLIC KEY` and save it in a file say `libsodium.key`:
5. Now run `sudo apt-key add libsodium.key`

[Courtesy: Askubuntu](http://askubuntu.com/a/358424)

Now run

```
sudo apt-get update
sudo apt-get install libsodium13
```

8. If you still get the error ```E: Unable to locate package libsodium13``` then add ```deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main``` and ```deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main``` to your ```/etc/apt/sources.list```. 
Now run ```sudo apt-get update``` and then ```sudo apt-get install libsodium13``` 

**CentOS/Redhat:**

1. Run ```sudo yum install python3.5```

2. Run ```sudo yum install libsodium-devel```


**Mac:**

1. Go to [python.org](https://www.python.org) and from the "Downloads" menu, download the Python 3.5.0 package (python-3.5.0-macosx10.6.pkg) or later.

2. Open the downloaded file to install it.

3. If you are a homebrew fan, you can install it using this brew command: ```brew install python3```

4. To install homebrew package manager, see: [brew.sh](http://brew.sh/)

5. Once you have homebrew installed, run ```brew install libsodium``` to install libsodium.


**Windows:**

1. Go to https://download.libsodium.org/libsodium/releases/ and download the latest libsodium package (libsodium-1.0.8-mingw.tar.gz is the latest version as of this writing)

2. When you extract the contents of the downloaded tar file, you will see 2 folders with the names libsodium-win32 and libsodium-win64.

3. As the name suggests, use the libsodium-win32 if you are using 32-bit machine or libsodium-win64 if you are using a 64-bit operating system.

4. Copy the libsodium-x.dll from libsodium-win32\bin or libsodium-win64\bin to C:\Windows\System or System32 and rename it to libsodium.dll.

5. Download the latest build (pywin32-220.win-amd64-py3.5.exe is the latest build as of this writing) from  [here](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/) and run the downloaded executable.


#### Using a virtual environment (recommended)
We recommend creating a new Python virtual environment for trying out Plenum.
a virtual environment is a Python environment which is isolated from the
system's default Python environment (you can change that) and any other
virtual environment you create. You can create a new virtual environment by:
```
virtualenv -p python3.5 <name of virtual environment>
```

And activate it by:

```
source <name of virtual environment>/bin/activate
```
