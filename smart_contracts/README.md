# Indy smart contracts

### Prerequisites to run

*  `node` > `v18.15.0` 
* `yarn`

### Install dependencies

```
> yarn install
```

### Compile contracts

```
> yarn compile
```

The following folders should be generated as the result: 
* `artifacts` - completed contract specification
* `typechain-types` - typescript bindings for contracts

### Run tests

```
> yarn test
```

### Contracts

* `contracts/RoleControl.sol` - contract to manage (assign/revoke) account roles.   
  * [RoleControl TS contract wrapper class](./scripts/contracts/role-control.ts)
* `contracts//ValidatorControl.sol` - contract to manage network validator nodes.
  * [ValidatorControl TS contract wrapper class](./scripts/contracts/validator-control.ts)

### Demos

You can find sample scripts demonstrating the usage of deployed contracts in the [demo folder](./demos).
* [Roles management](./demos/role-control.ts) - get/assign/revoke role to/from account.
    ```
    > yarn demo/roles
    ```
* [Validators management](./demos/validator-control.ts) - get list of current validators.
    ```
    > yarn demo/validators
    ```

### Helper Scripts

* `genesis` - helper scripts to generate genesis blocks for injecting contracts.
    
    > Find more details regarding the scripts in the [genesis section](#inject-contracts-into-network-genesis) of this document.

## Inject contracts into network genesis

### Prerequisites

* `socl` tool must be installed on the machine.

This section describes how to inject smart contracts into the genesis state of the network.

1. Prepare the [input file](scripts/genesis/config.ts) with the initial state of each contract.

3. Compile runtime contracts byte code:
   ```
   solc -o compiled-contracts --optimize --bin-runtime  --evm-version=constantinople  @dk1a=$(pwd)/node_modules/@dk1a @openzeppelin=$(pwd)/node_modules/@openzeppelin  contracts/**/*.sol node_modules/@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol
   ```
* `compiled-contracts` folder with binary files will be generated as the result of the execution.

2. Execute script generating the contracts content for the network genesis file:
   > yarn genesis/generate
  * `ContractsGenesis.json` file will be generated as the result

3. Put the whole block into the `alloc` section of the network genesis file.

4. Set address of `ValidatorControl` contract into `validatorcontractaddress` field of the `qbft` section of the genesis file.

4. Set address of `AccountControl` contract into `permissions-accounts-contract-address` field of the `config.toml` file.
