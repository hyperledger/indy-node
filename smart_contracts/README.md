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

This section describes how to inject a custom smart contract into the genesis state of the network.

#### Injecting Role control contract

1. Prepare the [input file](scripts/genesis/roles/data.json) with the initial state of the contract
  * `accounts`: list of objects containing account addresses and assigned roles
  * `roleOwners`: mapping of a role to the managing role

2. Execute script generating the contract content for the network genesis file:
   > yarn genesis/roles/generate
  * `RoleControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ./contracts/auth/RoleControl.sol
   ```
  * `RoleControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
  * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000006666`.
  * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

### Injecting Validator control contract and using it for QBFT consensus

**Note that ValidatorControl contract depends on RoleControl, which must be injected as well!**

1. Prepare the [input file](scripts/genesis/validators/data.json) with the initial state of the contract
  * `validators`: list of objects containing addresses of a validator owner and validator address
  * `roleControlContractAddress`: address of RoleControl contract

2. Execute script generating the contract content for the network genesis file:
   > yarn genesis/validators/generate
  * `ValidatorControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ./contracts/network/ValidatorControl.sol
   ```
  * `ValidatorControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
  * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000007777`.
  * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

6. Set address of ValidatorControl contract into `validatorcontractaddress` field of the `qbft` section of the genesis file.
