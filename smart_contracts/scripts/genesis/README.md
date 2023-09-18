# Using contracts in genesis config

This document describes how to inject a custom smart contract into the genesis state of the Besu network.

## Generate contract code for genesis file

#### Prerequisites 

* `yarn`
* `socl` tool must be installed on the machine.

### Injecting Role control contract into genesis network state

1. Prepare the [input file](roles/data.json) with the initial state of the contract
   * `accounts`: list of objects containing account addresses and assigned roles
   * `roleOwners`: mapping of a role to the managing role  

2. Execute script generating the contract content for the network genesis file:
    > yarn generate-roles
   * `RoleControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ../../RoleControl.sol
   ```
   * `RoleControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
   * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000006666`.
   * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

### Injecting Validator control contract into genesis network state and using it for QBFT consensus

1. Prepare the [input file](validators/data.json) with the initial state of the contract
   * `validators`: list of objects containing addresses of a validator owner and validator address
   * `roleControlContractAddress`: address of RoleControl contract

2. Execute script generating the contract content for the network genesis file:
   > yarn generate-validators
   * `ValidatorControlGenesis.json` file will be generated as the result

3. Generate runtime contract byte code:
   ```
   solc --optimize --bin-runtime --evm-version=byzantium -o . ../../ValidatorControl.sol
   ```
   * `ValidatorControl.bin-runtime` file will be generated as the result

4. Set values for placeholder variables:
   * `<Address of Contract>` - address of deployed contract. It can be any predefined address. For example: `0x0000000000000000000000000000000000007777`.
   * `<Contract Code>` - generated binary runtime code of the smart contract (step 3).

5. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.

6. Set address of ValidatorControl contract into `validatorcontractaddress` field of the `qbft` section of the genesis file.
