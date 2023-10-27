# Indy ledger

This project aims to provide a replacement for Hyperledger Indy blockchain that provides support for verifiable credentials.

## Design documentation

See [README.md](/docs/README.md).

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


