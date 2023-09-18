# Development guideline

## Prerequisites

- [Docker and Docker-compose](https://docs.docker.com/compose/install/) v2 or higher

⚠️ **Note**: If on MacOS or Windows, please ensure that you allow docker to use upto 4G of memory under the _Resources_ section. The [Docker for Mac](https://docs.docker.com/docker-for-mac/) and [Docker Desktop](https://docs.docker.com/docker-for-windows/) sites have details on how to do this at the "Resources" heading

## Run local pool

**To start services and the network:**

`./network/scripts/run.sh` starts all the docker containers

**To stop services :**

`./network/scripts/stop.sh` stops the entire network, and you can resume where it left off with `./resume.sh`

`./network/scripts/remove.sh ` will first stop and then remove all containers and images

## Manage smart contracts

See [README.md](./smart_contracts).
