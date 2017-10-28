![logo](collateral/logos/indy-logo.png)

* [About Indy Node](#About Indy Node)
* [Indy Node Repository Structure](#Indy Node Repository Structure)
* [Dependent Projects](#Dependent Projects)
* [Contact us](#Contact us)
* [How to Contribute](#How to Contribute)
* [How to Install a Test Network](#How to Install a Test Network)
* [How to Start Working with the Code](#How to Start Working with the Code)
* [Continues integration/delivery](#Continues integration/delivery)
* [How to send a PR](#How to send a PR)
* [How to Create a Stable Release](#How to Create a Stable Release)
* [How to Understand the Code](#How to Understand the Code)

## About Indy Node

This codebase embodies all the functionality to run nodes (validators and/or observers)
that provide a [self-sovereign identity ecosystem](https://sovrin.org) on top of a
distributed ledger. It is the core project for Indy; over time, all other indy-\* projects may
collapse into this one, except for [indy-sdk](https://github.com/hyperledger/indy-sdk).

##### Relationship with Sovrin
This code is independent from but commonly associated with [Sovrin](https://sovrin.org). Sovrin is a public utility
for identity, built on top of this codebase. People who install sovrin packages (e.g., with
`sudo apt install sovrin`) get prepackaged genesis transactions that integrate
with an Indy validator pool using [Sovrin's governance and trust framework](https://sovrin.org/wp-content/uploads/2017/06/SovrinProvisionalTrustFramework2017-03-22.pdf). However, it is possible to use Indy Node
with a different network, using whatever conventions a community chooses.

##### Getting Started Guide

- Today, documentation for Indy is sparse. Most materials that exist were written for Sovrin. Therefore,
we recommend that developers should explore Sovrin's [Getting Started Guide](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md) to learn about Indy Node basics. In the future, documentation
will be part of [indy-sdk](https://github.com/hyperledger/indy-sdk).

##### Hyperledger Wiki-Indy

- If you haven't done so already, please visit the main resource for all things "Indy" to get acquainted with the code base, helpful resources, and up-to-date information: [Hyperledger Wiki-Indy](https://wiki.hyperledger.org/projects/indy).

## Indy Node Repository Structure

Indy Node repo consists of the following parts:
- indy-node: 
    - [indy-plenum](https://github.com/hyperledger/indy-plenum)-based implementation of distributed ledger
    - Extends plenum's base pool functionality with specific transactions support (CLAIM_DEF, SCHEMA, POOL_UPGRADE, etc.)
- indy-client
    - Contains client and CLI code
    - Will be deprecated soon in favor of [indy-sdk](https://github.com/hyperledger/indy-sdk), so please use indy-sdk for your own applications dealing with Indy ecosystem.
- indy-common
    - Common code for both indy-node and indy-client parts.

## Dependent Projects

- [indy-plenum](https://github.com/hyperledger/indy-plenum)
    - The heart of the distributed ledger technology inside Hyperledger Indy.
    - Most probably you will need to make changes in Plenum if you want to contribute to Indy.
      So, if you want to work with Indy Node, you will need to have the Plenum code as well in most of the cases
      and work with two projects at the same time 
      (see How to work with the code below).
- [indy-anoncreds](https://github.com/hyperledger/indy-anoncreds) 
    - A python implementation of the anonymous credentials ideas developed by IBM Research.
    - This is quite independent from indy-node/plenum. So, in most cases you don't need this code to contribute to Indy-Node.
    - It will be deprecated soon in favor of anoncreds implementation in indy-sdk (see below). 
- [indy-sdk](https://github.com/hyperledger/indy-sdk)
    - An official SDK for Indy.
    - it contains client and anoncreds implementation
    - You don't need it to contribute to Indy-Node. But please use indy-sdk for your own applications dealing with Indy ecosystem.
    - It will replace indy-client and indy-anoncreds parsts soon.
- [indy-crypto](https://github.com/hyperledger/indy-crypto)
    - A shared crypto library 

## Contact us

- Bugs, stories, and backlog for this codebase are managed in [Hyperledger's Jira](https://jira.hyperledger.org).
Use project name `INDY`.
- Join us on [Jira's Rocket.Chat](https://chat.hyperledger.org/channel/indy) at `#indy` to discuss.


## How to Contribute

- We'd love your help; see these [instructions on how to contribute](http://bit.ly/2ugd0bq).
- You may also want to read this info about [maintainers](MAINTAINERS.md).


## How to Install a Test Network 

You can also have a look at [Start Nodes](#docs/start-nodes.md) 
to understand what needs to be done 

You can install a test network in one of several ways:

 - **Automated VM Creation with Vagrant** [Create virtual machines](https://github.com/evernym/sovrin-environments/blob/master/vagrant/training/vb-multi-vm/TestIndyClusterSetup.md) using VirtualBox and Vagrant.

 - **Docker** [Start Pool and Client with Docker](https://github.com/evernym/sovrin-environments/tree/master/docker)
 
 - **Running locally** [Running pool locally](#docs/Indy_Running_Locally.md)

 - **Also coming soon:** Create virtual machines in AWS.

The guides above provide a full and ready to use 

 


## How to Start Working with the Code

Please have a look at [Dev Setup](#docs/setup-dev.md)

## Continues integration/delivery

Please have a look at [ontinues integration/delivery](#docs/ci-cd.md)

## How to send a PR

If you made changes in both indy-plenum and indy-node, you need to do the following
- Raise a PR to indy-plenum's master, and wait until code is reviewed and merged. So, a new build of indy-plenum is created 
- Note a just built version of indy-plenum: X.Y.Z (you can check it either on tags/releases page, pypi or on CI server).
- Change indy-plenum's dependency version to the new one in indy-node's [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py).
- Raise PR to indy-node's master and wait until code is reviewed and merged. So, a new build of indy-node is created 


## How to Understand the Code

TBD







