This client is deprecated! Please, use the new libindy-based CLI: https://github.com/hyperledger/indy-sdk/tree/master/cli
________________________________________________________________________
# Getting Started

1. Bring up (or connect to) an OpenShift cluster.
2. Use the `oc_configure_builds.sh` and `oc_configure_deployments.sh` scripts to configure and deploy the 'Alice' example network in your OpenShift project.
3. Wait for the builds and deployments to complete.
4. Open a terminal to the client node.
5. Configure the agent nodes following the instructions here; [Starting the Indy Agent Scripts](../docker/pool/StartIndyAgents.md). *Ensure that you use the IP addresses assigned by openshift, not the default IP addresses in the instructions.*
6. Open a terminal to the client node and walk through the [Alice Gets a Transcript](../../getting-started.md#alice-gets-a-transcript) example.


## Prerequisites
* Docker
* OpenShift

## Starting and Stopping a local OpenShift Cluster

_Refer to [Chocolatey Scripts](https://github.com/WadeBarnes/dev-tools/tree/master/chocolatey) for information on setting up a location OpenShift environment._

To start a local cluster: `MSYS_NO_PATHCONV=1 ./oc_cluster_up.sh`

To stop a local cluster: `./oc_cluster_down`

## Description

Configuration and deployment scripts for deploying a sample network ready for the 'Alice' example in OpenShift.

### oc_configure_builds.sh

Use: `./oc_configure_builds.sh`

Creates the build configurations and image streams for the hyperledger indy images in OpenShift.

### oc_configure_deployments.sh

Use: `./oc_configure_deployments.sh`

Creates the deployment configurations, services, and routes for the hyperledger indy images in OpenShift.

## Status

By default the scripts setup a hyperledger indy network consisting of:
* 4 Indy Nodes
* 1 Client Node
* 3 Agent Nodes, one each for;
    * Faber
	* Acme
	* Thrift

All of the nodes are dynamically configured with the IP addresses of the Indy Nodes so they are able to connect and communicate.

Currently the agent configuration must be performed manually following the instructions here; [Starting the Indy Agent Scripts](../docker/pool/StartIndyAgents.md).  The plan is to script and automate the agent configuration and registration in a later version so the whole environment comes up in a state where the 'Alice' example can be run out of the box.
