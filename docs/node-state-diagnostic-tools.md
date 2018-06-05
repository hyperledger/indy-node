# Node State Diagnostic Tools Workflow

## Introduction
The Node state diagnostic tools are for working with indy node and its state. The tools are intended to work with
the recorder functionality and should help with diagnostic work in the development and QA work process on indy-node.
 
Current there three scripts and are located in tools/diagnostics. They are nscapture, nsreplay and nsdiff. We will 
document the basic functionally of the scripts and then describe the intended workflow.

This documentation is high level and will lack complete detail about the parameters and options for these scripts. 
Please see the '-h' output from the script for more details.

## nscapture

nscapture don't have any required parameters but does make the following assumptions that effect is behavior. Generally,
these assumptions should work in most production like environments (QA environments or other Debian install 
environments).
 
**Assumptions:**
1. ROOT_DIR: nscapture will assume that the root directory is base of the filesystem ('/'). This should be correct for 
Debian installed systems. For other installation patterns, the '-o' flag can be used to point to another location.
2. NODE_NAME: nscapture will look for nodes base on the root directory. If it only finds one node it will use that one.
If more than one node is found, nscapture will require the user to specify a node name to capture. For most system should 
only have one but if not, the '-n' options can be used to specify the desired node to capture.
3. OUTPUT_DIR: nscatpure will output the capture archive to the current working directory of the running process. If 
another location is desired, the '-o' option can be used. 

**Other Notes**
* Capture file name structure is:

```
<node name>.<pool name>.<capture date>.<file extension>

ex:
Node1.sandbox.20180517163819.tar.gz
```

This format is utilized by the other scripts.

## nsreplay
nsreplay can replay a nodes state capture archive if it contains a recording. nsreplay will start a single instance of 
indy-node and replay events (mostly messages). This script should be attachable to a debugger or other development 
tools. 

This script is mostly setting up the replay environment from the capture file and then using the replay code in Plenum 
enact the replay. 

**Assumptions**
1. HAS RECORDING: The replay requires a recording to replay. See doc/recorder.md in indy-plenum for how to 
configure the recorder. The recording can be found in the capture archive at ```data/<node name>/recorder/*```.

**Other Notes**

## nsdiff
nsdiff will compare two capture archives. The diff will highlight what parts of the Node state are different and how 
they differ. There are comments in the nsdiff script that list the different areas that are compared, but they include 
merkle leaves, merkle nodes, state and transactions for the different ledgers. 

nsdiff is intended as a tool to understand how node differs but will not replace deep understand of the Indy code base
to really make use of this tool.

nsdiff only requires two parameters which are the source of the two node states to compare. The node state can be 
a capture archive or directory containing the node state (this will be especially useful for the replay node state) 

**Assumptions**

**Other Notes**

# Workflow
The following is a simple but hopefully a common workflow for using these tools.
## Steps
### Step #1 - Configure recording
Add USE_WITH_STACK to indy_config.py and set to the value 1 (numeric value, NOT a String). 

The value 0 will DISABLE recording.

The value 1 will ENABLE recording.

Indy will require a restart for the configuration to take effect.
### Step #4 - Get indy into the desired state
Run load or other experiments to get the node into the desired state. This step is open-ended and up to the desire of
the person using the workflow.

### Step #3 - Capture Node state and recording
In the environment (on the server, VM, docker container, etc) where Indy is running, run nscapture. Doing this 
will produce an archive. This archive could be large depending on the state of the node. Every message for every 
instance will be contained in the recording. The archive must be moved to the environment where the replay will be 
performed. That can be done via SCP or similar method.

### Step #4 - Replay recording
In a development environment, us nsreplay to replay the recording. Currently, the replay will take a similar amount of 
time compared to the recording. During the replay, debugging and other development tools should be usable. 

### Step #5 - Diff captured Node state with replay state
If desired, the nsdiff can be used to check that the replay was able to reproduce the same state as the recording. 
Use nsdiff to check the difference between the states. Ideally, they will be identical but if they are different, 
insight might still be gained. 