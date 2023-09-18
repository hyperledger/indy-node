# Indy smart contracts

### Prerequisites to run

*  `node` > `v18.15.0` 
* `yarn`
* `socl` tool must be installed on the machine.

### Install dependencies

```
> yarn install
```

### Compile contracts

```
> yarn compile
```

The following folders should be generated: 
* `artifacts` - completed contract specification
* `typechain-types` - typescript bindings for contracts
* `contracts/<contract name's>.json` - generated contracts specification

### Run tests

```
> yarn test
```

### Contracts

* `contracts/RoleControl.sol` - contract to manage (assign/revoke) account roles.   
* `contracts//ValidatorControl.sol` - contract to manage network validator nodes.

### Scripts

* `genesis` - helper scripts to generate genesis blocks for injecting contracts.
  * Find more details regarding the steps in the genesis's [README.md file](scripts/genesis/README.md).
* `contracts` - sample scripts of calling deployed contracts.
* `compile.ts` - script to generate contract specification using `socl` and `hardhat. 
  * Run with `yarn compile`

## Inject contracts into network genesis

This section describes how to inject a custom smart contract into the genesis state of the network.

### Injecting Role control contract into genesis network state

1. Prepare the [input file](scripts/genesis/roles/data.json) with the initial state of the contract
  * `accounts`: list of objects containing account addresses and assigned roles
  * `roleOwners`: mapping of a role to the managing role

2. Execute script generating the contract content for the network genesis file:
   > yarn generate-roles-genesis
  * `RoleControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ./contracts/RoleControl.sol
   ```
  * `RoleControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
  * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000006666`.
  * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

### Injecting Validator control contract into genesis network state and using it for QBFT consensus

1. Prepare the [input file](scripts/genesis/validators/data.json) with the initial state of the contract
  * `validators`: list of objects containing addresses of a validator owner and validator address
  * `roleControlContractAddress`: address of RoleControl contract

2. Execute script generating the contract content for the network genesis file:
   > yarn generate-validators
  * `ValidatorControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ./contracts/ValidatorControl.sol
   ```
  * `ValidatorControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
  * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000007777`.
  * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

6. Set address of ValidatorControl contract into `validatorcontractaddress` field of the `qbft` section of the genesis file.
