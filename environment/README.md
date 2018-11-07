# Indy Environment
Methods and scripts for standing up Indy test environments for different use-cases.

The following are among the methods that can be used to set up a Indy Validator cluster for testing.  Others will be implemented in the future.

 - [Docker, multiple Containers](#docker)
 - [CloudFormation, multiple VMs](#cloudformation)
 - [Vagrant, multiple VMs (deprecated)](#vagrant)

## CloudFormation
Using the CloudFormation scripts, an admininstrator can create VPCs and VMs in AWS EC2. The scripts automate configuration tasks such as networking, installation of packages, and configuration of Indy Validator, Agent, and CLI client nodes.  The administrator must have an existing AWS account with adequate permissions, where he will paste in the CloudFormation script, modify it as necessary, and execute it.

## Docker
Using the Docker configuration and bash scripts, you can build and run Indy containers on your own PC (Linux, Mac, or Windows) docker environment, provided that it has adequate storage, memory, and CPU cores. The scripts automate the docker build process for Indy node and client images, and the steps for running the communicating containers. The only prerequisite is having a Docker installation running before executing the scripts. See the [ReadMe](docker/pool/README.md) for how to run the scripts, with additional details on starting the Agents (Faber College, etc.) needed for completing the Indy Tutorial - Alice and her Transcripts, Job, and Bank Applications.

## Util
A collection of utilities/scripts intended to be reused/reusable by all Indy environments. TODO: Decide how these utilities/scripts will be organized. It may be helpful to create a directory structure (component taxonomy/namespace) that aids in discovery.

## Vagrant
**Warning, this method has been deprecated and is no longer supported.** Using the Vagrant and bash scripts, an administrator can create VMs in his own PC (Linux, Mac, or Windows), provided that it has adequate storage, memory, and CPU cores.  The scripts automate installation and configuration of Indy software on the VMs, creating Indy Validator, Agent, and CLI client nodes.  Freely available VirtualBox and Vagrant software must be installed before executing these scripts.  The "[TestIndyClusterSetup.md](vagrant/training/vb-multi-vm/TestIndyClusterSetup.md)" file in the vagrant/training/vb-multi-vm/ directory documents the installation and use of the Vagrant scripts.



