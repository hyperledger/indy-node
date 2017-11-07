![logo](collateral/logos/indy-logo.png)

* [About Indy Node](#about-indy-node)
* [Indy Node Repository Structure](#indy-node-repository-structure)
* [Dependent Projects](#dependent-projects)
* [Contact us](#contact-us)
* [How to Contribute](#how-to-contribute)
* [How to Install a Test Network](#how-to-install-a-test-network)
* [How to Start Working with the Code](#how-to-start-working-with-the-code)
* [How to Start Indy Client CLI](#how-to-start-indy-client-cli)
* [Continues integration and delivery](#continues-integration-and-delivery)
* [How to send a PR](#how-to-send-a-pr)
* [How to Understand the Code](#how-to-understand-the-code)

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
    - Common code for both indy-node and indy-client parts
- scripts
    - Some scripts that can be run for installed Node (in particular, scripts to start Nodes, generate keys, prepare test Network, etc.)
- doc
    - a folder with documentation
- dev-setup
    - a folder with scripts helping to configure development environment (python, dependencies, projects, virtual environment)

## Dependent Projects

- [indy-plenum](https://github.com/hyperledger/indy-plenum)
    - The heart of the distributed ledger technology inside Hyperledger Indy.
    - Most probably you will need to make changes in Plenum if you want to contribute to Indy.
      So, if you want to work with Indy Node, you will need to have the Plenum code as well in most of the cases
      and work with two projects at the same time 
      (see [How to Start Working with the Code](#how-to-start-working-with-the-code) below).
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
    - It's based on [AMCL](https://github.com/milagro-crypto/amcl)
    - In particular, it contains BLS multi-signature crypto needed for state proofs support in Indy.

## Contact us

- Bugs, stories, and backlog for this codebase are managed in [Hyperledger's Jira](https://jira.hyperledger.org).
Use project name `INDY`.
- Join us on [Jira's Rocket.Chat](https://chat.hyperledger.org/channel/indy) at `#indy` and/or `#indy-node` channels to discuss.


## How to Contribute

- We'd love your help; see these [instructions on how to contribute](http://bit.ly/2ugd0bq).
- You may also want to read this info about [maintainers](MAINTAINERS.md).


## How to Install a Test Network 

You can have a look at [Start Nodes](docs/start-nodes.md) 
to understand what needs to be done to create a Network, initialize and start Nodes, and what scripts are provided for this.

The described process is automated in one of the ways below (it allow to install a test Network):

 - **Automated VM Creation with Vagrant** [Create virtual machines](https://github.com/evernym/sovrin-environments/blob/stable/vagrant/training/vb-multi-vm/TestIndyClusterSetup.md) using VirtualBox and Vagrant.

 - **Docker** [Start Pool and Client with Docker](https://github.com/evernym/sovrin-environments/tree/master/docker)
 
 - **Running locally** [Running pool locally](docs/indy-running-locally.md) or [Indy Cluster Simulation](docs/cluster-simulation.md)

 - **Also coming soon:** Create virtual machines in AWS.


## How to Start Working with the Code

Please have a look at [Dev Setup](docs/setup-dev.md)


## How to Start Indy Client CLI
Once installed, you can play with the command-line interface by running Indy from a terminal.

Note: For Windows, we recommended using either [cmder](http://cmder.net/) or [conemu](https://conemu.github.io/).
```
indy
```

## Continues Integration and Delivery

Please have a look at [Continues integration/delivery](docs/ci-cd.md)

## How to send a PR

If you made changes in both indy-plenum and indy-node, you need to do the following:
- Raise a PR to indy-plenum's master
    - Make sure that all your commits have a DCO sign-off from the author
    - Make sure that static code validation passed 
    (you can run `flake8 .` on the project root to check it; you can install flake8 from pypi: `pip install flake8`)
    - Put the link to the PR to `#indy-pr-review` channel in Rocket.Chat
    - A reviewer needs to review the code, approve it, start your tests (add `test this please` comment to the PR), and merge a PR (we usually use Squash) after all the tests pass.
    - So, a new build of indy-plenum is created 
- Note a just built version of indy-plenum (indy-plenum-dev in pypi): X.Y.Z (you can check it either on [tags/releases](https://github.com/hyperledger/indy-plenum/releases) page, [pypi](https://pypi.python.org/pypi/indy-plenum-dev) or on CI server).
- Change indy-plenum-dev's dependency version to the new one in indy-node's [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py).
- Raise PR to indy-node's master and wait until code is reviewed and merged (the same as described above).
    - So, a new build of indy-node is created 


## How to Understand the Code

- Indy-plenum is based on [RBFT](https://pakupaku.me/plaublin/rbft/5000a297.pdf) protocol
- [Indy Transaction Types](https://docs.google.com/spreadsheets/d/19A3u4Ba3OjDSHeJdLjtoGWLWHTSBk3Y15u13-67TIX4/edit#gid=657206024)
- [Network roles and permissions](https://docs.google.com/spreadsheets/d/1TWXF7NtBjSOaUIBeIH77SyZnawfo91cJ_ns4TR-wsq4/edit#gid=0)
- More TBD





