# Using a DApp to interact with the blockchain

This DApp, uses Hardhat and Ethers.js in combination with a self custodial (also called a user controlled) wallet i.e. Metamask to interact with the chain. As such this process esentially comprises two parts:

1. Deploy the contract to the chain
2. Use the DApp's interface to send and transact on the chain

The `dapps/quorumToken` folder is this structured in this manner (only relevant paths shown):

```
quorumToken
├── hardhat.config.ts       // hardhat network config
├── contracts               // sample contracts of which we use the QuorumToken.sol
├── scripts                 // handy scripts eg: to deploy to a chain
├── test                    // contract tests
└── frontend                // DApp done in next.js
  ├── README.md
  ├── public
  ├── src
  ├── styles
  ├── tsconfig.json
```

# Contracts

Contracts are written in Solidity and we use the hardhat development environment for testing, deploying etc

The `hardhat.config.js` specifies the networks, accounts, solidity version etc

Install dependencies

```
npm i
```

Compile the contracts and run tests (optional):

```
npx run compile
# As you develop contracts you are using the inbuilt `hardhat` network
npx hardhat test
```

Deploy contracts with:

```
# we specify the network here so the DApp can use the contract, but you can use any network you wish to and remember to connect Metamask to the appropriate network for the DApp
npx hardhat run ./scripts/deploy_quorumtoken.ts --network quickstart
```

_Please remember to save the address returned from the deploy as you will need it for the following steps_

# DApp

We have a sample DApp created that uses Next.js, react and ethers to interact with the quickstart network

```
cd frontend
npm i
npm run dev
```

1. Open up a tab on port 3001 and connect to Metamask.
2. To interact with the DApp you will need to import the test accounts from `hardhat.config.ts`

   For brevity they are the following:

   ```
   0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63
   0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3
   0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f
   ```

3. When you connect to Metamask, you are presented with a field to input the address of the deployed contract from the previous step. The app will then fetch the contract data and you can then transfer eth to a new another account.
