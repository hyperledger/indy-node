# Using custom Validator Control smart contracts

This document describes how to use custom smart contract implementation for managing validator nodes in QBFT consensus protocol implementation in Besu network.

## Create the genesis validators

1. Prepare the input file with the genesis validators data: 
   * account - owner account address 
   * validator - address of validator node
   > Example file: [initialValidators.json](initialValidators.json) 

2. Execute script that generates the content for the genesis file of the network:
  * `ValidatorsGenesis.json` file will be generated as the result 
  > yarn generate

3. Set values for placeholder variables:
   * `<Address of Contract>` - address of deployed contract. Identical value muse be set for `validatorcontractaddress` field in the `qbft` section of the genesis file.
   * `<Contract Code>` - generated binary runtime code for used smart contract.

4. Put the whole block of `"<Address of Contract>": {.....` into the `alloc` section of the network genesis file.
