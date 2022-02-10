# Setting up a New Network

## Introduction

   The purpose of this document is to describe in some detail the process of building a brand-new Indy Node Network (Network) using 4 Stewards on their own separate nodes.
   It goes into more details than [Starting a Network](../start-nodes.md).
   These instructions are intended to be used for a distributed or “production” level environment but can be adapted to be used to build a private network.

   This document is heavily based on [Create New Indy Network](https://docs.google.com/document/d/1XE2QOiGWuRzWdlxiI9LrG9Am9dCfPXBXnv52wGHorNE) and the [Steward Validator Preparation Guide v3](https://docs.google.com/document/d/18MNB7nEKerlcyZKof5AvGMy0GP9T82c4SWaxZkPzya4).

## I. Create Network Governance documents (Optional)

   Network Governance describes the policies and procedures by which your new network will run and be maintained. Here’s an example: [Sovrin Governance Framework](https://docs.google.com/document/d/1K8l5MfXQWQtpT49-FHuYn_ZnRC5m0Nwk)


## II. Assign Network Trustees
   
   Trustees are the people who manage the network and protect the integrity of the Network Governance.  This includes managing the `auth_rules`.

   For a production Network, at least 3 Trustees representing three different persons are required and more are preferred.  For a test Network one Trustee is required and 3 or more are preferred (all Trustee DID’s may belong to the same user on a test network if needed). 

   Initial Trustees (3 preferred) must create and submit a Trustee DID and Verkey so that the domain genesis file can be built.

   Each trustee has to [instal the `indy-cli`](./CLIInstall.md) and [create a Trustee DID](./CreateDID.md).

   Once the Trustees have created their DID and Verkey give the Trustees access to a spreadsheet like [this one](https://docs.google.com/spreadsheets/d/1LDduIeZp7pansd9deXeVSqGgdf0VdAHNMc7xYli3QAY/edit#gid=0) and have them fill out their own row of the Trustees sheet.  The completed sheet will be used to generate the genesis transaction files for the network.   


## III. Genesis Stewards

   A Steward is an organization responsible for running a Node on the Network

   Exactly 4 “Genesis” Stewards are needed to establish the network, more Stewards can be added later.

   Each Genesis Steward’s node information will be included in the Genesis Pool file, so they should be willing to install and maintain a Node on the new Network for an extended period of time.

   The Stewards must:
   1. Generate Steward DIDs as described in [Creating DID](./CreateDID.md).
   1. Install their node as described in [Installation and configuration of Indy-Node](../installation-and-configuration.md) (with some small adjustments):
      1. Determine a name for the new network and have the stewards substitute it in the appropriate places in the guide, such as when setting the network name and creating the directory when creating the keys for the node. This step MUST be completed before running init_indy_node as part of step [3.2.3 Create the Key for the Validator Node](https://github.com/lynnbendixsen/indy-node/blob/master/docs/source/installation-and-configuration.md#323-create-the-key-for-the-validator-node). 
      1. They all need to stop at the normal place ([3.5. Add Node to a Pool](../installation-and-configuration.md#3.5.-Add-Node-to-a-Pool)) as instructed in the guide as the steps that follow differ when creating a new network.  The following sections of this guide describe the steps required to start the new network.

   Once the Stewards have created their DID and Verkey, and performed the initial setup of they node, give the Stewards access to a spreadsheet like [this one](https://docs.google.com/spreadsheets/d/1LDduIeZp7pansd9deXeVSqGgdf0VdAHNMc7xYli3QAY/edit#gid=0) and have them fill out their own row of the Stewards sheet.  The completed sheet will be used to generate the genesis transaction files for the network.   

## IV. Create and Distribute genesis transaction files

   Save the sheets filled out by the Trustees and Stewards as separate files in csv format, and use the [genesis_from_files.py](https://github.com/sovrin-foundation/steward-tools/tree/master/create_genesis) script to generate the `pool_transactions_genesis` and `domain_transactions_genesis` files for the network.

   >Tip: The `generategenesisfiles` in `von-network` provides a convenient wrapper around the `genesis_from_files.py` and runs it in a container including all of the dependencies.  For more information refer to [Generate Genesis Files](https://github.com/bcgov/von-network/blob/main/docs/Indy-CLI.md#generate-genesis-files).

   Double check the files contain the correct information:
   - The `domain_transactions_genesis` file should contain all of the DIDs and Verkeys for the Trustees (`"role":"0"`) and the Stewards (`"role":"2"`).
   - The `pool_transactions_genesis` file should contain each of the nodes with all their unique information.
   
   Publish the genesis files to a public location, such as a GitHub repository associated with your network.  The Stewards and end users will need this information.

   Inform the Stewards and Trustees where they can download the genesis files.

   - The Trustees and Stewards will need to register the `pool_transactions_genesis` with their `indy-cli` to complete the setup and to be able to connect to the network once it's running.  How and where they need to register the `pool_transactions_genesis` depends on how they setup their `indy-cli` environment; [Installing the `indy-cli`](./CLIInstall.md)

   - The Stewards will also need to download the genesis files onto their nodes while completing the setup.  All of the following steps are to be completed on the node.
      1.  Set the network name in `/etc/indy/indy_config.py`, replacing `<the_network_name>` in the following command with the actual network name;
      
            `sudo sed -i -re "s/(NETWORK_NAME = ')\w+/\1<the_network_name>/" /etc/indy/indy_config.py`
      
      1. Create a network directory and download the genesis files into it.  _The directory name must be the same on all of the nodes and it must match the name of the network._
         1. `sudo -i -u indy mkdir /var/lib/indy/<the_network_name>`
         1. `cd  /var/lib/indy/<the_network_name>`
         1. `sudo curl -o domain_transactions_genesis <url_to_the_raw_domain_transactions_genesis_file>`
         1. `sudo curl -o pool_transactions_genesis  <url_to_the_raw_pool_transactions_genesis_file>`
         1. `sudo chown indy:indy *`
            - It is important the files are owned by `indy:indy`.
  
## V. Schedule a meeting to instantiate the new network

   Invite all Genesis Stewards to a meeting where they can execute commands and share their screens for both an `indy-cli` and for their Validator Nodes being added to the Network.
    
   > NOTE: It is very useful to go through some checks for each node to verify their setup before continuing. Some large amounts of debug and recovery work can be avoided by 5-10 minutes of checking configs of each node at the beginning of the meeting.
   > - `/etc/indy/indy_config.py`
   >   - all nodes need to have the same network name.
   >   - the name of the network should correspond to the `/var/lib/indy/<the_network_name>` directory on each node which contains the genesis files for the network, and the files in the directory should be owned by `indy:indy`.
   > - `/etc/indy/indy.env`
   >   - all nodes should have local ip addresses in this file and be pointing at the correct ports.
   > - Genesis files
   >   - Ensure both `pool_transactions_genesis` and `domain_transactions_genesis` files contain the expected content.
   > - Verify the software version on all the nodes match
   >   ```
   >   dpkg -l | grep indy
   >   dpkg -l | grep sovrin
   >   ```
   > - Network Connectivity
   >   - Use `nc -l <local_ip_address> <port>` (on the host), and `nc -vz <public_ip_address> <port>` (on the remote) to test the following.
   >     - Check the network connectivity between nodes using the `node_ip:port` combinations.  Ensure that each node can communicate with all of the other nodes.
   >     - Check the network connectivity between the nodes and a client using the `client_ip:port` combinations.  Ensure each node is accessible to client machines.

   Once all of the checks are complete have the Stewards simultaneously start their nodes as described in section [3.5.2. Enable the Service](../installation-and-configuration.md#3.5.2.-Enable-the-Service) of the Installation and configuration of Indy-Node guide, and walk though the remainder of that guide.

## VI. Configure the Indy Network

### `auth_rules`
   Update the network's `auth_rules` to help enforce the governance rules for the network.

   For more information on `auth_rules` refer to:
   - [Default AUTH_MAP Rules](../auth_rules.md)
   - [auth_rules Walkthough](https://docs.google.com/document/d/1xk0A5FljKOZ2Fazri6J5mAfnYWXdOMl2LwrFK16MJIY)

### `TAA` (Transaction Author Agreements)
   Add a `TAA` to the network.
   
   For more information on `TAA`s refer to:
   - [Transaction Author Agreement - `indy-sdk`](https://github.com/hyperledger/indy-sdk/blob/master/docs/how-tos/transaction-author-agreement.md)
   - [Transaction Author Agreement - `indy-plenum`](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/transaction_author_agreement.md)
   - [Transaction Author Agreement Design](../../../design/txn_author_agreement.md)
   - [TAA for CLI Walkthrough](https://docs.google.com/document/d/1Ma-EJkYpRfPOZApyEvcWrkb4EKn71XrIFd9KvZL0Whg)

## Where to go from here?

   ### Add more Nodes
   
   For the network to remain in write consensus in the event of node failures the network needs to be comprised of `3f+1` nodes, where `f` is the number of failed nodes.

   For a network of 4 nodes the network can remain in write consensus if a single node at a time fails, however if more than a single node fails at a time the network will loose write consensus and go into a read-only state.  Similarly, a network comprised of 7 nodes can withstand up to 2 nodes failing at any given time.  Therefore, it's recommended to have at least 7 nodes running in your network.

   Examples:

   | Failures to Withstand | 3f+1 | Required Nodes |
   |--|--|--|
   | 1 | 3(1)+1 | 4 |
   | 2 | 3(2)+1 | 7 |
   | 3 | 3(3)+1 | 10 |

   ### Network Monitoring

   [hyperledger/indy-node-monitor](https://github.com/hyperledger/indy-node-monitor) is the community supported and maintained tool for network monitoring.

   #### Manual
   - Run `indy-node-monitor` at least three times a day to detect any issues with the network.

   #### Automated
   - Run `indy-node-monitor` on a schedule (every 15-30 minutes) and add a notification plugin to alert you to any issues.  _Please consider contributing your work back to the project._

## Hands On Walkthrough

   An example walkthrough of the above mentioned steps can be found in the `sample/Network` [folder](../../../sample/Network/README.md).
