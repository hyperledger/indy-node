# Node State Diagnostic Tools Workflow

## Introduction
The Node state diagnostic tools are for working with indy node and its state.
The tools are intended to work with the recorder functionality and should help
with diagnostic work in the indy-node development and QA workflows.
 
There are currently three scripts located in tools/diagnostics. They are
nscapture, nsreplay and nsdiff. Basic functionality and intended workflow are
documented below.

This documentation is high level and will lack complete detail about the
parameters and options for these scripts.  Please see the '-h' output from the
script for more details.

## nscapture

nscapture has no required parameters and makes the following assumptions.
These assumptions should work in most production like environments (QA
environments or other Debian install environments).
 
**Assumptions:**
1. ROOT_DIR: nscapture will assume that the root directory is the base of the
filesystem ('/'). This should be correct for Debian installed systems. For other
installation patterns, the '-o' flag can be used to point to another location.
2. NODE_NAME: nscapture will look for nodes; starting it's search from the root
directory. If only one node configuration is found, nscapture will capture it.
Otherwise, nscapture will require the user to specify which node to capture.
Most nodes will only have one configuration. The '-n' option can be used to
specify the desired node to capture.
3. OUTPUT_DIR: By default, nscatpure will output the archive to the current
working directory of the running process. If another location is desired,
the '-o' option can be used. 

**Other Notes**
* Capture file name structure is:

```
<node name>.<pool name>.<capture date>.<file extension>

ex:
Node1.sandbox.20180517163819.tar.gz
```

This format is expected by the other scripts.

## nsreplay
If a node's nscapture archive contains a recording, nsreplay starts a single
instance of indy-node and replays captured events (mostly messages) using
replay logic in Plenum.

**Assumptions**
1. Node state was captured using nscapture.
2. HAS RECORDING: The replay requires a recording to replay. See doc/recorder.md
in indy-plenum for details on how to configure the recorder. nscapture captures
the recording in ```data/<node name>/recorder/*```.

**Other Notes**

## nsdiff
nsdiff will compare two nscapture archives. The result will highlight what parts
of the Node state are different and how they differ in *nix diff format. The
contents of the nscapture archives dictates what is being compared. What
nscapture captures for comparison may change over time. There are comments in
the nsdiff script that describe what is being compared and how to get a
comprehensive list of things being compared.

nsdiff is intended to help understand how node state differs between different
nodes in the same cluster or between a node and it's replayed state. It is not
inteneded to lessen/reduce the need for in-depth understanding of the Indy
codebase.

**Assumptions**
1. Node state was captured using nscapture.

**Other Notes**

# Workflow
The following is a simple but hopefully a common workflow for using these tools.
## Steps
### Step #1 - Configure recording
Add STACK_COMPANION to indy_config.py and set to the value to 1 (numeric value,
NOT a String). 

The value 0 will DISABLE recording.

The value 1 will ENABLE recording.

Indy will require a restart for the configuration to take effect.
### Step #2 - Get indy into the desired state
Run load or other experiments to get the node into the desired state. This step
is open-ended and up to the desires/objectives of the person using the workflow.

### Step #3 - Capture Node state and recording
In the environment (on the server, VM, docker container, etc) where Indy is
running, stop Indy (indy-node service) and then run nscapture. Doing this 
will produce an archive. This archive could be large depending on the state of
the node. Every message for every instance will be contained in the recording.
The archive must be moved to the environment where the replay will be performed.
That can be done via SCP or similar method.

### Step #4 - Replay recording
In a development environment, use nsreplay to replay the recording. Currently,
the replay will take a similar amount of time compared to the recording. During
the replay, debugging and other development tools should be usable. 

### Step #5 - Capture replayed Node state
In the environment (on the server, VM, docker container, etc) where nsreplay was
run, execute nscapture to capture the replayed state.

### Step #6 - Diff captured Node state with capatured replay state
If desired, the nsdiff can be used to check that the replay was able to
reproduce the same state as the recording.  Use nsdiff to check the difference
between the states. Ideally, they will be identical but if they are different, 
insight might still be gained. 
