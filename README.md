![logo](collateral/logos/indy-logo.png)
# Indy Node
* [About Indy Node](#about-indy-node)
* [Technical Overview of Indy Blockchain](#technical-overview-of-indy-blockchain)
* [Indy Node Repository Structure](#indy-node-repository-structure)
* [Dependent Projects](#dependent-projects)
* [Contact us](#contact-us)
* [How to Contribute](#how-to-contribute)
* [How to Install a Test Network](#how-to-install-a-test-network)
* [How to Start Working with the Code](#how-to-start-working-with-the-code)
* [Continuous integration and delivery](https://github.com/hyperledger/indy-node/blob/master/docs/source/ci-cd.md)
* [How to send a PR](#how-to-send-a-pr)
* [Docs and links](#docs-and-links)

## About Indy Node

This codebase embodies all the functionality to run nodes (validators and/or observers)
that provide a [self-sovereign identity ecosystem](https://sovrin.org) on top of a
distributed ledger. It is the core project for Indy; over time, all other indy-\* projects may
collapse into this one, except for [indy-sdk](https://github.com/hyperledger/indy-sdk).

Indy has its own distributed ledger based on RBFT.

##### Relationship with Sovrin
This code is independent from but commonly associated with [The Sovrin Foundation](https://sovrin.org). The Sovrin Foundation is a public utility
for identity, built on top of this codebase. People who install sovrin packages (e.g., with
`sudo apt install sovrin`) get prepackaged genesis transactions that integrate
with an Indy validator pool using [Sovrin's governance and trust framework](https://sovrin.org/wp-content/uploads/2018/03/Sovrin-Provisional-Trust-Framework-2017-06-28.pdf). However, it is possible to use Indy Node
with a different network, using whatever conventions a community chooses.

##### Getting Started Guide

- We recommend that developers should explore Sovrin's [Getting Started Guide](https://github.com/hyperledger/indy-sdk/blob/master/docs/getting-started/indy-walkthrough.md) to learn about Indy basics.

##### Hyperledger Wiki-Indy

- If you haven't done so already, please visit the main resource for all things "Indy" to get acquainted with the code base, helpful resources, and up-to-date information: [Hyperledger Wiki-Indy](https://wiki.hyperledger.org/projects/indy).

## Technical Overview of Indy Blockchain
Please visit [Technical Overview of Plenum](https://github.com/hyperledger/indy-plenum/blob/master/docs/main.md).

More documentation can be found in [indy-plenum-docs](https://github.com/hyperledger/indy-plenum/blob/master/docs)
and [indy-node-docs](docs/source/).

## Indy Node Repository Structure

Indy Node repo consists of the following parts:
- indy-node:
    - [indy-plenum](https://github.com/hyperledger/indy-plenum)-based implementation of distributed ledger
    - Extends plenum's base pool functionality with specific transactions support (CLAIM_DEF, SCHEMA, POOL_UPGRADE, etc.)
- indy-common
    - Common code for indy-node
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
- [indy-sdk](https://github.com/hyperledger/indy-sdk)
    - An official SDK for Indy.
    - it contains client and anoncreds implementation
    - You don't need it to contribute to Indy-Node. But please use indy-sdk for your own applications dealing with Indy ecosystem.
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
- See [How to send a PR](#how-to-send-a-pr) below.


## How to Install a Test Network

You can have a look at [Start Nodes](docs/source/start-nodes.md)
to understand what needs to be done to create a Network, initialize and start Nodes, and what scripts are provided for this.

The described process is automated in one of the ways below (it allow to install a test Network):

 - **Docker** [Start Pool with Docker](environment/docker/pool/README.md)

 - **Docker-based pool using with new libindy-based CLI**:
   - [Start Pool Locally](https://github.com/hyperledger/indy-sdk/blob/master/README.md#how-to-start-local-nodes-pool-with-docker)
   - [Get Started with Libindy](https://github.com/hyperledger/indy-sdk/blob/master/doc/getting-started/getting-started.md)

 - **Also coming soon:** Create virtual machines in AWS.



## How to Start Working with the Code

Please have a look at [Dev Setup](docs/source/setup-dev.md)


## Continuous Integration and Delivery

Please have a look at [Continuous integration/delivery](docs/source/ci-cd.md)

## How to send a PR

- Make sure that you followed [write code guideline](docs/source/write-code-guideline.md) before sending a PR
- Do not create big PRs; send a PR for one feature or bug fix only.
 If a feature is too big, consider splitting a big PR to a number of small ones.
- Consider sending a design doc into `design` folder (as markdown or PlantUML diagram) for a new feature  before implementing it
- Make sure that a new feature or fix is covered by tests (try following TDD)
- Make sure that documentation is updated according to your changes
- Provide a full description of changes in the PR including Jira ticket number if any
- Make sure that all your commits have a DCO sign-off from the author
- Make sure that static code validation passed
(you can run `flake8 .` on the project root to check it; you can install flake8 from pypi: `pip install flake8`)
- Put the link to the PR into `#indy-pr-review` channel in Rocket.Chat
- A reviewer needs to start your tests first (add `test this please` comment to the PR)
- You need to make sure that all the tests pass
- A reviewer needs to review the code and approve the PR. If there are review comments, they will be put into the PR itself.
- You must process them (feel free to reply in the PR threads, or have a discussion in Rocket.Chat if needed)
- A reviewer or maintainer will merge the PR (we usually use Squash)


#### How to send a PR to both plenum and node
If you made changes in both indy-plenum and indy-node, you need to do the following:
- Raise a PR to indy-plenum's master and wait until code is reviewed and merged (see above)
    - So, a new build of indy-plenum is created
- Note a just built version `X.Y.Z.devB` of indy-plenum (you can check it in [pypi](https://pypi.python.org/pypi/indy-plenum) or on CI server).
- Change indy-plenum's dependency version to the new one in indy-node's [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py).
- Raise PR to indy-node's master and wait until code is reviewed and merged (see above)
    - So, a new build of indy-node is created


## Docs and links

- Indy-plenum is based on [RBFT](https://pakupaku.me/plaublin/rbft/5000a297.pdf) protocol
- Please have a look at documents and diagrams in [docs/source](docs/source) folder
- Please have a look at documents and diagrams in Plenum's [docs](https://github.com/hyperledger/indy-plenum/tree/master/docs) folder, or on https://indy.readthedocs.io/projects/plenum :
    - [Technical Overview of Plenum](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/main.md)
    - [Plenum Consensus Algorithm Diagram](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/diagrams/consensus-protocol.png)
    - [Glossary](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/glossary.md)
    - [Storages](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/storage.md)
    - [Request Handling](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/request_handling.md)
    - [Catchup](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/catchup.md)
    - [Catchup Diagram](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/diagrams/catchup-procedure.png)
    - [Plugins](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/plugins.md)
- Relationship between Entities and Transactions: [relationship diagram](docs/source/relationship-diagram.png)
- Supported transactions and their format: [transactions](docs/source/transactions.md)
- Supported requests (write, read) and their format: [requests](docs/source/requests.md)
- [Network roles and permissions](https://github.com/hyperledger/indy-node/blob/master/docs/source/auth_rules.md)
- [Indy file folder structure guideline](docs/source/indy-file-structure-guideline.md)
- [Helper Scripts](docs/source/helper-scripts.md)
- [Pool Upgrade](docs/source/pool-upgrade.md)
- [Node Addition](docs/source/add-node.md)
