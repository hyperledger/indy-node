# Sovrin – Running the Getting Started tutorial locally

## Overview

Currently, out of the box, the Getting started tutorial uses externally running nodes and assumes that these are all up and running.  However, being test nodes, sometimes they aren’t, or sometimes you just want to see everything flowing through in a local environment.

This guide describes the process of setting up a local 4 node cluster, attaching an agent to the cluster (Faber in this case), and running a client (Alice).

It (currently) supports the GettingStarted tutorial up to to point of accepting Fabers claim however adding the Acme and ThriftBank agents is pretty trivial).

Note - I'm still trying to get my head around the details of Sovrin so there may be a few things I'm doing wrong or haven't yet understood! However this process is working nicely so far.
 

## Requirements

I’m assuming that you have Sovrin-node installed (I recommend installing this in an Ubuntu Virtual Machine if possible) – If not follow the instructions at: https://github.com/sovrin-foundation/sovrin-node/blob/master/setup.md

Finally make sure that `pytest` module is installed (it is required to run test-related functionality like Faber, Acme and ThriftBank test agents): 

```
pip install pytest
```

## Initial setup
In your home folder, create a Sovrin folder. In here we are going to put the scripts we will use to setup the environment. Then change into this folder.

So first, we need to create our nodes.

Create a script ```setupEnvironment.sh``` containing:

```
# Remove .sovrin folder 
rm -rf ~/.sovrin

# Create nodes and generate initial transactions
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 1
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 2
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 3
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 4

echo Environment setup complete
```

This first clears out the ~/.sovrin folder (if it exists), creates 4 nodes and then generates all the necessary initial transactions and Stewards.

Make the script executable (chmod 744 setupEnvironment.sh).

At this point you are ready to build your environment.

## Start nodes

So, if you run the setupEnvironent.sh script, you should see a whole lot of output of the nodes and transactions being created.

At this point you are now ready to start the nodes.

Open up 4 new terminal windows and in each one run one of the following commands (one in each window):
```
start_sovrin_node Node1 9701 9702
start_sovrin_node Node2 9703 9704
start_sovrin_node Node3 9705 9706
start_sovrin_node Node4 9707 9708
```

This will start each node running and with luck, they will connect to each other, do their handshaking and will elect a master and backup.
At this point you have a nice 4 node Sovrin cluster running.


## Attach Faber agent to cluster

Before we can connect the Faber agent to the cluster, we have to register (onboard) it with the cluster first.
To do this, we connect to the cluster as a Steward (a trusted entity that was created earlier as part of the generate transactions process),
register the Faber agents identifier (NYM) and also register the agents endpoint as an attribute against the NYM.

So, first we start the Sovrin CLI using the command ```sovrin```

Then run the following commands:
```
new key with seed 000000000000000000000000Steward1
connect test
send NYM dest=FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB role=TRUST_ANCHOR
send ATTRIB dest=FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB raw={"endpoint": {"ha":"127.0.0.1:5555"}}
```

We first add the Stewards key into the Keyring (this enables us to assume the Steward role) - Note this key is hardcoded into the test scripts at the moment so is pre-generated
We then connect to the test Sovrin cluster (which is the one we are running locally)
Then we registers Fabers identifier and set its role as a Trust Anchor (A Trust Anchor is a privilege which if possessed by an identifier allows that identifier to on-board other identifiers)
Finally we then register an attribute containing the endpoint for the Faber identifier.

At this point we can start the Faber agent.

This is fairly simple, and you start it using the command:
```
python ~/.virtualenvs/sovrin/lib/python3.5/site-packages/sovrin_client/test/agent/faber.py --port 5555
```
Note - the above assumes you set up a Python virtual environment called sovrin as per the installation guide). If not, this should be the path the the faber.py script.

The Faber agent should then start up, connect to our test Sovrin cluster, handshake and be accepted as a Trust Anchor.

## Run Getting Started guide

At this point, you can follow the Getting Started guide at https://github.com/sovrin-foundation/sovrin/blob/master/getting-started.md up to the point of Applying for a Job.
I recommend you use a seperate Sovrin CLI instance for this.

If you wish to add the Acme and ThriftBank agents, follow the steps for attaching the Faber agent using the following infomation:

I've included the full steps for the getting started console commands in the Getting Started Steps section
### ACME Client
```
send NYM dest=7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21 role=TRUST_ANCHOR
send ATTRIB dest=7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21 raw={"endpoint": {"ha":"127.0.0.1:6666"}}

python ~/.virtualenvs/sovrin/lib/python3.5/site-packages/sovrin_client/test/agent/acme.py --port 6666
```

### ThriftBank Client
```
send NYM dest=9jegUr9vAMqoqQQUEAiCBYNQDnUbTktQY9nNspxfasZW role=TRUST_ANCHOR
send ATTRIB dest=9jegUr9vAMqoqQQUEAiCBYNQDnUbTktQY9nNspxfasZW raw={"endpoint": {"ha":"127.0.0.1:7777"}}

python ~/.virtualenvs/sovrin/lib/python3.5/site-packages/sovrin_client/test/agent/thrift.py --port 7777
```


# Resetting the Sovrin environment

If you wish to reset your Sovrin environment and recreate it again, you can remove your ```~/.sovrin``` folder.

Then, when you want to re-create your environment from scratch, ensure that all the nodes and agents are stopped and just run the setupEnvironment.sh script.
Then you can restart the Nodes, attach the agents and away you go again.

# Getting Started Steps
This section just lists the commands from the Getting Started guide that should be run through.
These should be run in on a new Sovrin CLI instance.

```
prompt Alice
connect test

show sample/faber-invitation.sovrin
load sample/faber-invitation.sovrin
sync faber
show link faber
accept invitation from faber

show claim Transcript
request claim Transcript
show claim Transcript

show sample/acme-job-application.sovrin
load sample/acme-job-application.sovrin
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

show sample/thrift-loan-application.sovrin
load sample/thrift-loan-application.sovrin
sync thrift
accept invitation from thrift

show proof request Loan-Application-Basic
send proof Loan-Application-Basic to Thrift Bank

show proof request Loan-Application-KYC
send proof Loan-Application-KYC to Thrift Bank
```
