# Indy ledger

## Goals and ideas

* Provide a replacement for [Hyperledger Indy](https://www.hyperledger.org/projects/hyperledger-indy) ecosystem that provides support for verifiable credentials:
  * Components to replace:
    * Distributed ledger: [Indy Node](https://github.com/hyperledger/indy-node) and [Indy Plenum](https://github.com/hyperledger/indy-plenum)
    * Client library: [Indy SDK](https://github.com/hyperledger/indy-sdk/tree/main)
  * Capability to migrate the data from the original Indy Ledger
* Distributed ledger requirements:
  * Public Permissioned Blockchain
    * Control the validator nodes 
    * Control the user permissions
  * EVM compatible Blockchain
    * Capability to deploy on different networks
  * Based on existing open-source blockchain framework with a good performance, sufficient adoption, and wide community
  * Capability to work without tokens and fees
  * Stable consensus protocol
* Functional requirements:
  * Interoperability:
    * Capability to use existing DID's and identifiers:
      * Support [indy](https://hyperledger.github.io/indy-did-method/) DID method  
      * Support [sov](https://sovrin-foundation.github.io/sovrin/spec/did-method-spec-template.html) DID method
      * Identifiers previously stored on the client side should be resolvable on the new Ledger
    * Capability to use the ledger as an [AnonCreds Registry](https://hyperledger.github.io/anoncreds-methods-registry/)
    * Compatibility with the latest [AnonCreds Specification](https://hyperledger.github.io/anoncreds-spec/)
  * Extensibility: 
    * Capability to integrate new pieces of functionality easily
    * Capability to use [ETHR](https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md) DID method
      * Integration with the [AnonCreds Registry](https://hyperledger.github.io/anoncreds-methods-registry/)
      * Integration with `Permissioned` modules
  * Data validity:
    * Neglect `gas` efficiency in favour general validation of the stored data
      * Basic [DID Documents](https://www.w3.org/TR/did-core/) validation
      * Basic [AnonCreds entities](https://hyperledger.github.io/anoncreds-spec/#anoncreds-setup-data-flow) validation
      * Basic state consistency validation

## Design documentation

See [design document](./docs/README.md) covering the main ledger aspects.

## Running local network

### Prerequisites

- [Docker and Docker-compose](https://docs.docker.com/compose/install/) v2 or higher

> ⚠️ **Note**: If on MacOS or Windows, please ensure that you allow docker to use upto 4G of memory under the _Resources_ section. The [Docker for Mac](https://docs.docker.com/docker-for-mac/) and [Docker Desktop](https://docs.docker.com/docker-for-windows/) sites have details on how to do this at the "Resources" heading

### Commands

* **Start the network: - run all services inside the docker containers**
    ```bash
    ./network/scripts/run.sh
    ```

* **Stop the network: run the entire network, and you can resume where it left off with `./resume.sh`**
    ```bash
    ./network/scripts/stop.sh
    ```

* **Remove the network: stop and then remove all containers and images**
    ```bash
    ./network/scripts/remove.sh
    ```

## Managing smart contracts

See [README.md](/smart_contracts/README.md).


