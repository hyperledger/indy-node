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

### Run tests

```
> yarn test
```

### Generate contract code for genesis file

* `socl` tool must be installed on the machine.

```
solc --optimize --bin-runtime --evm-version=byzantium -o . ./<contract_name.sol>
```

### Contracts

* `DidRegistry.sol` - DID's registry.
* `RoleControl.sol` - contract to manage (assign/revoke) account roles.   
* `ValidatorsControl.sol` - contract to manage network validator nodes.

### Scripts

* `genesis/validators` - helper script to generate genesis data for `ValidatorsControl.sol` smart contract.
* `public` - sample script calling deployed contract.
* `compile.js` - script to generate contract specification using `socl`  
