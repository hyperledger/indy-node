# Node State Diagnostic Tools Workflow

## Introduction
The Node state diagnostic tools are for working with indy node and its state. The tools are intended to work with
the recorder functionality and should help with diagnostic work in the development and QA work process on indy-node.
 
Current there three scripts and are located in tools/diagnostics. They are nscapture, nsreplay and nsdiff. We will 
document the basic functionally of the scripts and then describe the intended workflow. 

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
* Capture file name structor is:

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

**Assumptions**
1. HAS RECORDING: The replay requires a recording to replay. See doc/recorder.md in indy-plenum for how to 
configure the recorder. The recording can be found in the capture archive at ```data/<node name>/recorder/*```.

**Other Notes**

## nsdiff
comments

**Assumptions**

**Other Notes**

# Workflow
