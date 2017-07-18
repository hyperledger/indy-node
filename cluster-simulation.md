# Running a Simulation of a Sovrin Cluster and Agents
One way to run through the [Sovrin Getting Started Guide](getting-started.md) is to set up a simulation of a Sovrin Validator Cluster.  This simulation resides in a single process on a single PC, but it sets up multiple asynchronous call-backs, one for each node being simulated.  These call-backs are handled sequentially in an event loop.  This gives the approximate performance of nultiple Sovrin Validator, Agent and CLI client nodes, but all running within a single process.  These instructions will configure the simulation, leaving you at the end with a CLI command-line prompt that you can use to complete the Getting Started Guide.

## Install the Sovrin Client Software

```
$ pip install -U --no-cache-dir sovrin-client
```

If you get any error, check out the info about [prerequisites](https://docs.google.com/document/d/1CyggP4nNPyx4SELNZEc2FOeln6G0F22B37cAVtB_FBM/edit); there are a few dominoes you might have to line up.


The install puts some python modules on your system. Most importantly, it gives you a command - line interface(CLI) to Sovrin. We are going to use that CLI to explore what Sovrin can do. (Sovrin also has a programmatic API, but it is not yet fully formalized, and this version of the guide doesn’t document it. See the [Sovrin roadmap](https://github.com/sovrin-foundation/sovrin/wiki/Roadmap).)

## Setup Environment
We will be doing this exercise in a Python Interactive Console. **_Sovrin must be run with Python 3._** So depending on your system setup, the next command could change.

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
>>> from sovrin_client.test.training.getting_started import *
```

### Run the Sovrin Cluster Simulation

Type this command:

```
>>> start_getting_started()
```

This command will start up a local pool of validator "nodes". This can take a few mintues and will produce a lot of console
output. This output contains the initial communication between 4 nodes. This output can be ignored for this exercise.
 
After starting up the local sovrin pool, three agents will be launched in virtual "nodes". During this this exercise we will be interacting
with three agents, Faber Collage, Acme Corp and Thrift Bank. Again, launching these agents can take some time and a lot of
output.

After these tasks are complete, you should see an interactive prompt, like this:

```
Sovrin - CLI version 1.17(c) 2016 Evernym, Inc.
Type 'help' for more information.
sovrin> 
```
You can now proceed with the Getting Started Guide, using this Sovrin client prompt.
