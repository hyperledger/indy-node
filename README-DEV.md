# Development guideline

## Prerequisites

- [Docker and Docker-compose](https://docs.docker.com/compose/install/) v2 or higher

⚠️ **Note**: If on MacOS or Windows, please ensure that you allow docker to use upto 4G of memory under the _Resources_ section. The [Docker for Mac](https://docs.docker.com/docker-for-mac/) and [Docker Desktop](https://docs.docker.com/docker-for-windows/) sites have details on how to do this at the "Resources" heading

## Run local pool

**To start services and the network:**

`./run.sh` starts all the docker containers

**To stop services :**

`./stop.sh` stops the entire network, and you can resume where it left off with `./resume.sh`

`./remove.sh ` will first stop and then remove all containers and images

## Write and compile a smart contract

1) Create a new solidity smart contract in `smart_contracts/contracts` directory
2) Run `compile` script 
    ```
    cd smart_contracts
    npm run compile
    ```

## Deploy smart contract and send transaction

1) Create new `deploy smart contract and send transaction` script in `smart_contracts/scripts/public` directory
2) Exec the script from point 3: `node <script name>.js`

## Make a transaction

```
cd smart_contracts
npm install
node scripts/public/<your script name>.js
```