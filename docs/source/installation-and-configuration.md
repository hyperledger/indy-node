# Installation and configuration of Indy-Node

## 1. Introduction
The purpose of this document is to describe how to setup a production level Indy-Validator-Node and register it on an existing network using an `indy-cli` machine which you also configure along the way.  This documentation is based heavily on the [Sovrin Steward Validator Preparation Guide v3](https://docs.google.com/document/d/18MNB7nEKerlcyZKof5AvGMy0GP9T82c4SWaxZkPzya4).

For information on how to setup a new network, refer to [New Network](./NewNetwork/NewNetwork.md)

## 2. Preliminaries to the Set Up
Before you start this process, you’ll need to gather a couple of things and make a few decisions. 

As you proceed through these steps, you will be generating data that will be needed later. As you follow the instructions and obtain the following, store them for later use:

- Your Steward Seed
  - This is extremely important, and it must be kept safe and private. It is used to generate the public / private key pair that you will use as a Steward to post transactions to the ledger. 
- Your Steward distributed identity (DID)
  - This is public information that is generated based on your Steward Seed. It is an identifier for your organization that will be written to the ledger by an Indy network Trustee. 
- Your Steward verification key (verkey)
  - This is public information that is generated based on your Steward Seed. It will be written to the ledger by an Indy network Trustee along with your DID, and will be used to verify transactions that you write to the ledger
- The Validator IP Address for inter-node communications
  - This IP address must be configured for exclusive use of inter-node consensus traffic. Ideally, traffic to this address will be allow-listed in your firewall.
- The Validator node port
- The Validator IP Address for client connections
  - This IP address must be open for connections from anywhere, since clients around the world will need to be able to connect to your node freely.
- The Validator client port
- The Validator alias
  - A human readable name for your node.  This value is case sensitive.
- The Validator node seed
  - This is distinct from your Steward seed and will be used to generate public and private keys that your Validator node will use for communications with other Validators. Like the Steward Seed, it should be kept secure.
- The Validator Node Identifier
  - This is distinct from your Steward verkey. It is also public information that will be placed on the ledger but is used as a public key by your Validator node, rather than by you, the Steward. 
- The Validator BLS public key. 
  - Used by the Validator to sign individual transactions that will be committed to the ledger. It is public information that will be written to the ledger.
- The Validator BLS key proof-of-possession (pop)
  - A cryptographic check against certain forgeries that can be done with BLS keys.

### 2.1 Two Machines
You’ll need two machines: one is your Validator node and the other an `indy-cli` machine to run the `indy-cli` with which you will interact with the ledger. They can be physical machines, virtual machines, or a combination. The machine with the `indy-cli` can be turned on and off at your convenience (refer to [3.1. `indy-cli` Machine Installation](##3.1.-indy-cli-Machine-Installation) for more details), only the Validator node needs to be public and constantly running.

>Important: for security reasons, you must not use your Validator node as an `indy-cli` client.  If you do, it could expose your Steward credentials needlessly.

Your Validator **must run Ubuntu 16.04 (64-bit)** as, _at the time of writing_, this is the only version that has a verified and validated release package.  Work is actively being done on an Ubuntu 20.04 release.  This guide presupposes that your `indy-cli` machine will run on Ubuntu as well.

Your Validator node should have two NICs, each with associated IP addresses and ports. One NIC will be used for inter-validator communication, and the other for connections from clients, including Indy edge agents, as well as ssh and other connections you use for administration. This two NIC approach is required as a defense against denial-of-service attacks, since the NIC for inter-validator communications should be behind a firewall that is configured to be much more restrictive of inbound connections than the client-facing NIC is.

It is currently possible to have just one NIC and IP address, as the transition for older Stewards to change to 2 NICs is ongoing. The inability to or delay of adding a second NIC will likely affect which network your node will be placed on. A resource that may help you to configure your node to use two NICs is described ind [Configuring a 2 NIC Node](./configuring-2nics.md)

### 2.2 Validator Node Preliminary Information

#### Get the IP Addresses
Your Validator node will be the machine that will become a part of an Indy network. It should have two static, publicly accessible, world routable IP addresses. It should be configured so that outgoing TCP/IP connections are from these same addresses, as well as incoming connections.

Obtain IP addresses that meet this requirement. 

#### Choose Port Numbers
The Validator node will also be required to have the following: 

- Node Port: TCP 
  - The Validators use this IP address and port combination to communicate with each other. 
- Client Port: TCP 
  - Clients use this IP address and port combination to communicate with the Validator node, to interact with the ledger.

By convention, please choose ports 9701 and 9702 for your Node and Client ports, respectively. 

#### Choose an Alias:
Your Validator node will need to have an alias. This will be used later when we create a key for the node. It can be any convenient, unique name that you don’t mind the world seeing. It need not reference your company name; however it should be distinguishable from the other Validator nodes on the network. Many Stewards choose a Validator alias that identifies their organization, for pride of their contribution to the cause of self-sovereign identity.


## 3. Setup and Configuration

Some instructions must be executed on the Validator node, and others on the `indy-cli` machine. The command line prompts in the instructions will help remind you which machine should be used for each command.

### 3.1. `indy-cli` Machine Installation

The following instructions describe how to install and configure the `indy-cli` directly on a machine or VM. The other, possibly more convenient, option is to use a containerized `indy-cli` environment like the one included with [von-network](https://github.com/bcgov/von-network).  For information on how to use the containerized `indy-cli` in `von-network`, refer to [Using the containerized indy-cli](https://github.com/bcgov/von-network/blob/main/docs/Indy-CLI.md)

#### 3.1.1. Install the `indy-cli`
On the machine you’ve chosen for the `indy-cli`, open a terminal and run the following lines to install the `indy-cli` package.

```
ubuntu@cli$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
ubuntu@cli$ sudo apt-get install -y software-properties-common python-software-properties
ubuntu@cli$ sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable"
ubuntu@cli$ sudo add-apt-repository "deb https://repo.sovrin.org/deb xenial stable"
ubuntu@cli$ sudo apt-get update -y
ubuntu@cli$ sudo apt-get upgrade -y
ubuntu@cli$ sudo apt-get install -y indy-cli
```

#### 3.1.2. Add an Acceptance Mechanism
To write to an Indy Node Ledger, you’ll need to sign the Transaction Author Agreement (TAA). You can learn more about the TAA [here](https://github.com/hyperledger/indy-sdk/blob/master/docs/how-tos/transaction-author-agreement.md). This agreement is incorporated into the process of connecting to the node pool and requires an acceptance mechanism. For the `indy-cli`, the default mechanism is “For Session” and the following instructions are required to be able to use “For Session” for your `indy-cli`:

Create a JSON config file containing your taaAcceptanceMechanism. (You can also add plugins to this config file, but for now just set it up as basic as possible.)

This example cliconfig.json file contains the line that sets the AML:
```json
{
"taaAcceptanceMechanism": "for_session" 
}
```

To start the `indy-cli` using your new config file, run the following:
`ubuntu@cli$ indy-cli --config <path_to_cfg>/cliconfig.json`

Now all of the appropriate transactions will have an “Agreement Accepted” authorization attached to them during this `indy-cli` session.

#### 3.1.3. Obtain the Genesis Files
Obtain the genesis transaction files for the Network with the following steps. For the sake of this documentation, we will use the genesis files from the Sovrin Networks. Information on how to create a genesis file can be found [here](./NewNetwork/NewNetwork.md).  These files contain bootstrap information about some of the Validator nodes, which will be used by your `indy-cli` to connect to the networks.

If you are at the `indy` prompt, please exit:

`indy> exit`

Most Stewards will currently be onboarded to the BuilderNet. Obtain the genesis transaction file for it:

`ubuntu@cli$ cd `

`ubuntu@cli:~ $ curl -O https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_builder_genesis`

You will also want to obtain the genesis files for the StagingNet and MainNet, for the possibility of moving between networks:

```
ubuntu@cli:~ $ curl -O https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_sandbox_genesis
ubuntu@cli:~ $ curl -O https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_live_genesis
```

#### 3.1.4. Generate the Steward Key
Next, generate a Steward key using the `indy-cli` machine you just installed. This will be comprised of a public and private key pair, generated from a seed. Knowing your seed will allow you to regenerate the key on demand. To keep this secure, you will need to have a very secure seed that is not easy to guess. 

##### Generate a Seed
>WARNING:
You want to guard your seed well. The seed will be used to generate your public (verification) key as well as your secret private key. If your seed falls into the wrong hands, someone could regenerate your private key, and take over your identity on the ledger. Keys can be rotated, which can stop some of the damage, but damage will still have been done. 

>Note:
It is the same procedure as described in [CreateDID](./NewNetwork/CreateDID.md).

In the terminal, run the following to install a good random string generator, and then use it to generate your seed: 
```
ubuntu@cli$ sudo apt install pwgen
ubuntu@cli$ pwgen -s 32 1
```
EXAMPLE:
```
ubuntu@cli$ pwgen -s 32 -1
ShahXae2ieG1uibeoraepa4eyu6mexei 
```

>IMPORTANT:
Keep this seed in a safe place, such as an encrypted password manager or other secure location designated by your organization. You will need it later in this guide, as well as in the future for other Steward interactions with the ledger. 

##### Run the `indy-cli` and generate key
Next we run the `indy-cli` by entering: 

`ubuntu@cli$ indy-cli --config <path_to_cfg>/cliconfig.json`

In the command line, enter the following to create your pool configuration and your wallet locally. In these instructions, we use "buildernet" for the pool name and "buildernet_wallet" for the wallet name, although you may use other names of your choosing, if desired. The encrypted wallet will be used to store important information on this machine, such as your public and private keys. When creating your wallet, you will need to provide a "key" that is any string desired. It will be the encryption key of your local wallet.

```
indy> pool create buildernet gen_txn_file=pool_transactions_builder_genesis
indy> wallet create buildernet_wallet key
```
Upon entering this command, you’ll see a prompt to enter your wallet key. Enter the key and hit enter.

>IMPORTANT:
To be able to retain your wallet and not re-create it when you need it in the future, keep this wallet key in a secure location as well. 

Using the pool configuration and wallet you have created, connect to the pool and open the wallet:

`indy> pool connect buildernet`

When you connect to a Network with TAA enabled, you will be asked whether you want to view the Agreement.  Type ‘y’ to accept to see the Agreement, then select ‘y’ again to accept the Agreement displayed. If you do not accept the agreement, then you will not be allowed to write to the Network.

`indy> wallet open buildernet_wallet key`

`<enter the key when prompted>`

Using the seed that you generated with pwgen, place your public and private keys into your wallet.

`indy> did new seed`

`<enter the seed when prompted>`

The result should look something like this: 

`Did "DIDDIDDIDDIDDIDDIDDID" has been created with "~VERKEYVERKEYVERKEYVERKEY" verkey`

>IMPORTANT: Save the “DID”  and “verkey” portions of this. They are not secret, but they will be used when you are prompted to supply your Steward verkey and DID. 

### 3.2 Validator Node Installation
#### 3.2.1. Perform Network Test
This test is to confirm that your Validator node can connect with external devices. 

Note that the communication protocol used for both node and client connections is ZMQ. If your firewall uses deep packet inspection, be sure to allow this protocol bi-directionally.

The tests in this section are to ensure your node's networking is operational, and that firewalls will allow TCP traffic to and from your IP addresses and ports. The assumptions are that for this stage of testing, you will be able to reach both sets of IP address/port combinations from an arbitrary client, but that later you will implement rules on your firewall restricting access to your node (inter-validator) IP address/port.

##### 3.2.1.1 Test the node (inter-validator) connection to your Validator
Use netcat to listen on the "node" IP address and port of your Validator

>IMPORTANT:
Many providers, such as AWS, use local, non-routable IP addresses on their nodes and then use NAT to translate these to public, routable IP addresses. If you are on such a system, use the local address to listen on, and the public address to ping with.

`ubuntu@validator$ nc -l <node_ip_address> <node_port> `

The above command will wait for a connection. On a system that can be used as a client, such as your `indy-cli` machine, do a TCP ping of that IP address and port:

`ubuntu@cli$ nc -vz <node_ip_address> <node_port>`

If the test is successful, the ping will return a "succeeded" message and the commands on both nodes will exit.

##### 3.2.1.2 Test the client (edge agent) connection to your Validator
Repeat the above test on your Validator and a test client but using the Validator's "client" IP address and port.

>Important: The “client” IP address referred to here is not the `indy-cli` machine’s IP address. Reminder:  The Validator node has a node IP address for communications with other Validators and a “client” IP address for communications with edge agents (anything outside the Network of Validators).

On your Validator:

`ubuntu@validator$ nc -l <client_ip_address> <client_port> `

On your client:

`ubuntu@cli$ nc -vz <client_ip_address> <client_port>`

If the test is successful, the ping will return a "succeeded" message and the commands on both nodes will exit.

>IMPORTANT:
If your system uses NAT, the same approach should be used as above.

##### 3.2.1.3 Test the connection from your node to another Validator on the BuilderNet
One of the Validator nodes on the BuilderNet is named "FoundationBuilder", which has a node IP address and port of 50.112.53.5 and 9701, respectively. On your Validator, make sure that your node is able to connect to this node on BuilderNet by TCP pinging its node IP address and port:

```
ubuntu@validator$ nc -vz 50.112.53.5 9701
Connection to 50.112.53.5 9701 port [tcp/*] succeeded!
```
When the above three tests are successful, you may proceed.

#### 3.2.2 Install the Validator Node
Continue on your Validator node machine.

>Important:  You must use a login user with sudo privileges (**not root or indy**) to run these commands, unless otherwise indicated.

```
ubuntu@validator$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
ubuntu@validator$ sudo apt-get install -y software-properties-common 
ubuntu@validator$ sudo add-apt-repository "deb https://repo.sovrin.org/deb xenial stable"
ubuntu@validator$ sudo apt update 
ubuntu@validator$ sudo apt upgrade -y
ubuntu@validator$ sudo apt install -y sovrin
```
#### 3.2.3 Create the Key for the Validator Node

>IMPORTANT:
Many providers, such as AWS, use local, non-routable IP addresses on their nodes and then use NAT to translate these to public, routable IP addresses. If you are on such a system, use the local addresses for the init_indy_node command.

Please run the following on the Validator before running `init_indy_node`.

In the `/etc/indy/indy_config.py` file, change the Network name from “sandbox” (Sovrin StagingNet) to “net3” (Sovrin BuilderNet) (use sudo to edit the file or use `sudo sed -i -re "s/(NETWORK_NAME = ')\w+/\1net3/" /etc/indy/indy_config.py)` then run the following commands:  
Note: **This is where you would substitute the directory name of the new network if you were setting up a new network.**
```
sudo -i -u indy mkdir /var/lib/indy/net3
cd /var/lib/indy/net3
sudo curl -o domain_transactions_genesis https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/domain_transactions_builder_genesis 
sudo curl -o pool_transactions_genesis  https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_builder_genesis 
```
Make sure that both genesis files are owned by `indy:indy` by running:

`sudo chown indy:indy *`

Enter the following where `<ALIAS>` is the alias you chose for your Validator node machine and `<node ip>, <client IP>,  <node port #> and <client port #>` are the correct values for your Validator. 

>Note: The node IP and client IP addresses should be the LOCAL addresses for your node.

`ubuntu@validator$ sudo -i -u indy init_indy_node <ALIAS> <node ip> <node port> <client ip> <client port>`

You will see something like this: 
```
Node-stack name is Node19
Client-stack name is Node19C
Generating keys for random seed b'FA7b1cc42Da11B8F4BC83990cECF63aD'
Init local keys for client-stack
Public key is a9abcd497631de182bb6f767ffb4921cdf83ffdb20e9d22e252883b4fc34bf2f
Verification key is 3d604d22c4bbfd55508a5a7e0008847bdeccd98a41acd048b500030020629ee1
Init local keys for node-stack
Public key is a9abcd497631de182bb6f767ffb4921cdf83ffdb20e9d22e252883b4fc34bf2f
Verification key is bfede8c4581f03d16eb053450d103477c6e840e5682adc67dc948a177ab8bc9b
BLS Public key is 4kCWXzcEEzdh93rf3zhhDEeybLij7AwcE4NDewTf3LRdn8eoKBwufFcUyyvSJ4GfPpTQLuX6iHjQwnCCQx4sSpfnptCWzvFEdJnhNSt4tJMQ2EzjcL9ewRWi24QxAaCnwbm2BBGJXF7JjqFgMzGfuFXXHhGPX3UtdfAphrojk3A1sgq
Proof of possession for BLS key is QqPuAnjnkYcE51H11Tub12i7Yri3ZLHmEYtJuaH1NFYKZBLi87SXgC3tMHxw3LMxErnbFwJCSdJKbTb2aCVmGzqXQtVWSpTVEQCsaSm4SUZLbzWVoHNQqDJASRYNbHH2CqpR2MtntA4YNb2WixNSZNXFSdHMbB1yMQ7XUcZqtGHhcb
```

**Store the original command, the random seed, the verification key, the BLS public key, and the BLS key proof-of-possession (POP).** These are the keys for your Validator node (not to be confused with the keys for you in your Steward role). The Validator verification key and BLS key (with its POP) are public and will be published on the ledger. 

>The random seed should be protected from disclosure.

### 3.3 Run the Technical Verification Script
>Note:
These steps are only required for becoming a Steward in Sovrin Networks.
However, you could incorporate this process into your own Network registration procedures.

Download this script and set the execution flag on it:

```
ubuntu@validator$ cd ~
ubuntu@validator$ curl -O https://raw.githubusercontent.com/sovrin-foundation/steward-tools/master/steward_tech_check.py
```
`ubuntu@validator$ chmod +x steward_tech_check.py`

Execute it, answering the questions that it asks.  There are no wrong answers; please be honest.  Questions that can be answered by scripting are automatically completed for you.

`ubuntu@validator$ sudo ./steward_tech_check.py`

After the script completes, copy the output beginning at '== Results for "A Steward MUST" ==', and send the results to the support team of the related network for review.

### 3.4. Provide Information to Trustees
At this point you should have the following data available: 

- Your Steward verkey and DID
- The Validator ‘node IP address’
- The Validator ‘client IP address’
- The Validator ‘node port’
- The Validator ‘client port’
- The Validator alias
- The Validator verkey
- The BLS key and Proof of possession (pop)

### 3.5. Add Node to a Pool 

>DO NOT proceed further with this document until your Steward DID and verkey (the public key) is on the ledger.  

#### 3.5.1 Configuration
After you have been informed that your public key has been placed onto the ledger of the Network, you may complete the configuration steps to activate your Validator node on that network.

Things to verify before activating the node:  
Note: If you are creating a new network, substitute the new networks directory name for 'net3' below.
- `cat /etc/indy/indy_config.py`
  - Ensure the network configuration is correct.
- `cat /etc/indy/indy.env`
  - Verify the node alias and IPs
- `cat /var/lib/indy/net3/domain_transactions_genesis`
  - Verify the file contains the correct content.
- `cat /var/lib/indy/net3/pool_transactions_genesis`
  - Verify the file contains correct content.

##### Make Sure Your Version Is Current
In some cases, some time may have passed before reaching this point. You should ensure that you have the current version of indy software installed before proceeding. On the Validator node, execute the following.

Verify Versions
```
dpkg -l | grep indy
```

##### Add Validator Node to Ledger
On your `indy-cli` machine, if you are not still on the `indy-cli` prompt, you will need to return to it. To get back to where you were, type `indy-cli --config <path_to_cfg>/cliconfig.json`, connect to the network pool, designate the wallet to use (using the same wallet key as before), and enter the DID that was returned earlier, when you typed `did new seed` (then enter your seed) for your Steward user: 

```
ubuntu@cli$ indy-cli --config <path_to_cfg>/cliconfig.json
indy> pool connect buildernet
indy> wallet open buildernet_wallet key=<wallet_key>
indy> did use <your_steward_DID>
```

>Note: You may need to create a new wallet and run `did new seed` then enter `<your_steward_seed>` instead, if you did not save your wallet or forgot your wallet key.

If the connection is successful, enter the following, substituting the correct data as appropriate.  An example follows. 

>Suggestion: Edit this in a text editor first, then copy and paste it into the `indy-cli`. Some editors will insert 'smart quotes' in place of regular ones.  This will cause the command to fail.

>IMPORTANT:
Many providers, such as AWS, use local, non-routable IP addresses on their nodes and then use NAT to translate these to public, routable IP addresses. If you are on such a system, use the routable public addresses for the ledger node command.

```
indy> ledger node target=<node_identifier> node_ip=<validator_node_ip_address> node_port=<node_port> client_ip=<validator_client_ip_address> client_port=<client_port> alias=<validator_alias> services=VALIDATOR blskey=<validator_bls_key> blskey_pop=<validator_bls_key_pop>
```

Example:
```
indy> ledger node target=4Tn3wZMNCvhSTXPcLinQDnHyj56DTLQtL61ki4jo2Loc node_ip=18.136.178.42 client_ip=18.136.178.42 node_port=9701 client_port=9702 services=VALIDATOR alias=Node19 blskey=4kCWXzcEEzdh93rf3zhhDEeybLij7AwcE4NDewTf3LRdn8eoKBwufFcUyyvSJ4GfPpTQLuX6iHjQwnCCQx4sSpfnptCWzvFEdJnhNSt4tJMQ2EzjcL9ewRWi24QxAaCnwbm2BBGJXF7JjqFgMzGfuFXXHhGPX3UtdfAphrojk3A1sgq blskey_pop=QqPuAnjnkYcE51H11Tub12i7Yri3ZLHmEYtJuaH1NFYKZBLi87SXgC3tMHxw3LMxErnbFwJCSdJKbTb2aCVmGzqXQtVWSpTVEQCsaSm4SUZLbzWVoHNQqDJASRYNbHH2CqpR2MtntA4YNb2WixNSZNXFSdHMbB1yMQ7XUcZqtGHhcb 
```

>Suggestion: Save this command.  You will use it again if you later move to another Network.

#### 3.5.2. Enable the Service
In the Validator node:

Return to the Validator node machine. 

Start the Validator service: 

`ubuntu@validator$ sudo systemctl start indy-node`

Verify the start:

`ubuntu@validator$ sudo systemctl status indy-node.service`

Enable the service so that it will auto-restart when your node reboots:

`ubuntu@validator$ sudo systemctl enable indy-node.service`

### 3.6. See if the Node Is Working
If the setup is successful, your Validator node now connects to the Validator pool.

In the Validator node:
`ubuntu@validator$ sudo validator-info`

If your node is configured properly, you should see several nodes being selected as the primary or its backups, as in this example:

    England (1)
    Singapore (3)
    Virginia (4)
    RFCU (5)
    Canada (0)
    Korea (2)


>Note: A ledger with a lot of transactions on it, like what often exists on the BuilderNet, can take a lot of time to sync up a new Validator node. If you don't get the right results for this test right away, try it again in a few minutes.

To check that messages and connections are occurring normally you can run the following commands to follow the log file: 
In the Validator node:

`ubuntu@validator$ sudo tail -f /var/log/indy/net3/<validator_alias>.log`

