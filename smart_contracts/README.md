## Commands

### Prerequisites to run

* Node > `v16.15.0` 

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
* `<contract name's>.json` - generated contracts specification

### Run tests

```
> yarn test
```

### Contracts

* `RoleControl.sol` - contract to manage (assign/revoke) account roles.   
* `ValidatorControl.sol` - contract to manage network validator nodes.

### Scripts

* `genesis` - helper scripts to generate genesis blocks for injecting contracts.
  * Find more details regarding the steps in the genesis's [README.md file](scripts/genesis/README.md).
* `contracts` - sample scripts of calling deployed contracts.
* `compile.ts` - script to generate contract specification using `socl` and `hardhat. 
  * Run with `yarn compile`
