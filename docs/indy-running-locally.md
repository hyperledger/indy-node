# Indy – Running the Getting Started tutorial locally

## Overview

Currently, out of the box, the [Getting Started](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md) tutorial uses externally running nodes and assumes that these are all up and running.
However, being test nodes, sometimes they aren’t, or sometimes you just want to see everything flowing through in a local environment.

This guide describes the process of setting up a local 4 node cluster and attaching the 3 Agents required [use the Indy CLI](https://github.com/hyperledger/indy-node/blob/master/getting-started.md#using-the-indy-cli) and impersonate Alice.


## Requirements

It's recommended to use an Ubuntu Virtual Machine and virtual environment if possible. 
Please follow the [setup-dev](https://github.com/hyperledger/indy-node/blob/master/docs/setup-dev.md) instruction for pre-requisites and dependencies.
As for installation of indy-node, it's recommended to create a separate virtual environment and install indy-node there as
```
pip install indy-node-dev
```

Finally make sure that `pytest` module is installed (it is required to run test-related functionality like Faber, Acme and ThriftBank test agents):

```
pip install pytest
```

## Initial setup
In your home folder, create an Indy folder. In here we are going to put the scripts we will use to setup the environment. Then change into this folder.

First of all we need to create basic folder structure. It could be done with the following command

```
create_dirs.sh
```
Please note, that you need ```root``` privileges to run the script. the script will create directories and grant current user full access rights
```
/etc/indy - main config directory
/var/lib/indy - main data directory
/var/log/indy - main log directory
```

Now we are ready to create our nodes.

Create a script ```setupEnvironment.sh``` containing:

```
# Remove .indy folder
rm -rf ~/.indy


# Create nodes and generate initial transactions
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 2 3 4


echo Environment setup complete
```

This first clears out the ~/.indy folder (if it exists), creates 4 nodes and then generates all the necessary initial transactions and Stewards.

Make the script executable (chmod +x setupEnvironment.sh).

At this point you are ready to build your environment.

## Start nodes

So, if you run the setupEnvironent.sh script, you should see a whole lot of output of the nodes and transactions being created.

At this point you are now ready to start the nodes.

Open up 4 new terminal windows and in each one run one of the following commands (one in each window):
```
start_indy_node Node1 9701 9702
start_indy_node Node2 9703 9704
start_indy_node Node3 9705 9706
start_indy_node Node4 9707 9708
```

This will start each node which should connect to each other, do their handshaking and will elect a master and backup.
At this point you have a nice 4 node Indy cluster running.

## Attach Agents to the cluster

Before we can connect the Faber, Acme and Thrift Agents to the cluster, we have to register (onboard) them with the cluster first.
To do this, we have to type the following commands using the Indy CLI tools started by typing ```indy```:

1. Add the Steward key into the Keyring to assume the Steward role. Which is a trusted entity that was created earlier as part of the generate transactions process. Its key seed has been hardcoded into the test scripts at the moment so is pre-generated:
```
new key with seed 000000000000000000000000Steward1
```
2. Connect to the cluster as this Steward to the test Indy cluster we are running locally:
```
connect sandbox
```
3. Register each Agent identifier (NYM) with the Trust Anchor role which allows to on-board other identifiers:
```
send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=TRUST_ANCHOR verkey=~5kh3FB4H3NKq7tUDqeqHc1
send NYM dest=CzkavE58zgX7rUMrzSinLr role=TRUST_ANCHOR verkey=~WjXEvZ9xj4Tz9sLtzf7HVP
send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=TRUST_ANCHOR verkey=~3sphzTb2itL2mwSeJ1Ji28
```
4. Impersonate each Agent owner (using pre-generated key seeds like for the Steward) and register its endpoint as an attribute against the NYM.
```
new key with seed Faber000000000000000000000000000
send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={"endpoint": {"ha": "127.0.0.1:5555", "pubkey": "5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z"}}

new key with seed Acme0000000000000000000000000000
send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={"endpoint": {"ha": "127.0.0.1:6666", "pubkey": "C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ"}}

new key with seed Thrift00000000000000000000000000
send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={"endpoint": {"ha": "127.0.0.1:7777", "pubkey": "AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x"}}
```

At this point we can start the Agents as follows, using separate sessions/windows (using [screen](https://www.gnu.org/software/screen/) for instance).

```
python /usr/lib/python3.5/site-packages/indy_client/test/agent/faber.py --port 5555
python /usr/lib/python3.5/site-packages/indy_client/test/agent/acme.py --port 6666
python /usr/lib/python3.5/site-packages/indy_client/test/agent/thrift.py --port 7777
```
REM: you may have to change the path to your Python interpreter and the libraries according to your environment (i. e.: ```/bin/python3.5 ~/.virtualenvs/indy/lib/python3.5/site-packages/indy_client/test/agent/...```).

Each Agent should then start up, connect to our test Indy cluster, handshake and be accepted as a Trust Anchor.

## Run Getting Started guide

At this point, you can follow the Getting Started guide from [Using Indy CLI](https://github.com/hyperledger/indy-node/blob/master/getting-started.md#using-the-indy-cli).
I recommend you use a seperate Indy CLI instance for this.

Here are the resulting commands ready to copy/paste:

```
prompt Alice
connect test

show sample/faber-invitation.indy
load sample/faber-invitation.indy
sync faber
show link faber
accept invitation from faber

show claim Transcript
request claim Transcript
show claim Transcript

show sample/acme-job-application.indy
load sample/acme-job-application.indy
sync acme
accept invitation from acme

show proof request Job-Application
set first_name to Alice
set last_name to Garcia
set phone_number to 123-45-6789
show proof request Job-Application
send proof Job-Application to Acme

show link acme

request claim Job-Certificate
show claim Job-Certificate

show sample/thrift-loan-application.indy
load sample/thrift-loan-application.indy
sync thrift
accept invitation from thrift

show proof request Loan-Application-Basic
send proof Loan-Application-Basic to Thrift Bank

show proof request Loan-Application-KYC
send proof Loan-Application-KYC to Thrift Bank
```

# Resetting the Indy environment

If you wish to reset your Indy environment and recreate it again, you can run ```clear_node.py --full```.

Then, when you want to re-create your environment from scratch, ensure that all the nodes and agents are stopped and just run the setupEnvironment.sh script.
Then you can restart the Nodes, attach the agents and away you go again.
