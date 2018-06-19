# Running a Simulation of a Indy Cluster and Agents
One way to run through the [Indy Getting Started Guide](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md) is to set up a simulation of a Indy Validator Cluster.  This simulation resides in a single process on a single PC, but it sets up multiple asynchronous call-backs, one for each node being simulated.  These call-backs are handled sequentially in an event loop.  This gives the approximate performance of multiple Indy Validator, Agent and CLI client nodes, but all running within a single process.  These instructions will configure the simulation, leaving you at the end with a CLI command-line prompt that you can use to complete the Getting Started Guide.

## Install the Indy Client Software

```
$ pip install -U --no-cache-dir indy-client
```

If you get any error, check out the info about [prerequisites](setup-dev.md); there are a few dominoes you might have to line up.


The install puts some python modules on your system. Most importantly, it gives you a command - line interface(CLI) to Indy. We are going to use that CLI to explore what Indy can do. (Indy also has a programmatic API, but it is not yet fully formalized, and this version of the guide doesn’t document it. See the [Indy roadmap](https://github.com/hyperledger/indy/wiki/Roadmap).)

## Setup Environment
We will be doing this exercise in a Python Interactive Console. **_Indy must be run with Python 3._** So depending on your system setup, the next command could change.

To launch Python Interactive Console, type this command:

```
$ python3
```
or
```
$ python
```

### Imports
You now have a Python prompt.  Using the prompt, only one import is required. This import will in turn import other modules and will provide helper functions for this exercise.  Any function with the prefix 'demo' are defined in this import and are just functions to help with the exercise.

```
>>> from indy_client.test.training.getting_started import *
```

### Run the Indy Cluster Simulation

Type this command:

```
>>> start_getting_started()
```

This command will start up a local pool of validator "nodes". This can take a few minutes and will produce a lot of console
output. This output contains the initial communication between 4 nodes. This output can be ignored for this exercise.

After starting up the local indy pool, three agents will be launched in virtual "nodes". During this this exercise we will be interacting
with three agents, Faber Collage, Acme Corp and Thrift Bank. Again, launching these agents can take some time and a lot of
output.

After these tasks are complete, you should see an interactive prompt, like this:

```
Indy - CLI version 1.17(c) 2016 Evernym, Inc.
Type 'help' for more information.
indy>
```
You can now proceed with the Getting Started Guide, using this Indy client prompt.
