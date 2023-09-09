const path = require('path');
const fs = require('fs-extra');
var ethers = require('ethers');

// RPCNODE details
const { tessera, besu } = require("../keys.js");
const host = besu.rpcnode.url;
const accountPrivateKey = besu.rpcnode.accountPrivateKey;

// abi and bytecode generated from simplestorage.sol:
// > solcjs --bin --abi simplestorage.sol
const contractJsonPath = path.resolve(__dirname, '../../','contracts','Counter.json');
const contractJson = JSON.parse(fs.readFileSync(contractJsonPath));
const contractAbi = contractJson.abi;
const contractBytecode = contractJson.evm.bytecode.object

async function getValueAtAddress(provider, deployedContractAbi, deployedContractAddress){
  const contract = new ethers.Contract(deployedContractAddress, deployedContractAbi, provider);
  const res = await contract.getCount();
  console.log("Obtained value at deployed contract is: "+ res);
  return res
}

// You need to use the accountAddress details provided to Quorum to send/interact with contracts
async function incrementValueAtAddress(provider, wallet, deployedContractAbi, deployedContractAddress){
  const contract = new ethers.Contract(deployedContractAddress, deployedContractAbi, provider);
  const contractWithSigner = contract.connect(wallet);
  const tx = await contractWithSigner.incrementCounter();
  // verify the updated value
  await tx.wait();
  // const res = await contract.get();
  // console.log("Obtained value at deployed contract is: "+ res);
  return tx;
}

async function decrementValueAtAddress(provider, wallet, deployedContractAbi, deployedContractAddress){
  const contract = new ethers.Contract(deployedContractAddress, deployedContractAbi, provider);
  const contractWithSigner = contract.connect(wallet);
  const tx = await contractWithSigner.decrementCounter();
  // verify the updated value
  await tx.wait();
  // const res = await contract.get();
  // console.log("Obtained value at deployed contract is: "+ res);
  return tx;
}

async function createContract(provider, wallet, contractAbi, contractByteCode) {
  const feeData = await provider.getFeeData();
  const factory = new ethers.ContractFactory(contractAbi, contractByteCode, wallet);
  const contract = await factory.deploy({
    chainId: 1337,
    type: 2,
    maxPriorityFeePerGas: feeData["maxPriorityFeePerGas"], 
    maxFeePerGas: feeData["maxFeePerGas"], 
  });
  // The contract is NOT deployed yet; we must wait until it is mined
  const deployed = await contract.waitForDeployment();
  //The contract is deployed now
  return contract
};

async function main(){
  const provider = new ethers.JsonRpcProvider(host);
  const wallet = new ethers.Wallet(accountPrivateKey, provider);

  createContract(provider, wallet, contractAbi, contractBytecode)
  .then(async function(contract){
    console.log(contract);
    contractAddress = await contract.getAddress();
    console.log("Use the smart contracts 'get' function to read the contract's initialized value .. " )
    await getValueAtAddress(provider, contractAbi, contractAddress);
    console.log("Use the smart contracts 'increment' function to update that value .. " );
    await incrementValueAtAddress(provider, wallet, contractAbi, contractAddress );
    console.log("Verify the updated value that was set .. " )
    await getValueAtAddress(provider, contractAbi, contractAddress);
    console.log("Use the smart contracts 'decrement' function to update that value .. " );
    await decrementValueAtAddress(provider, wallet, contractAbi, contractAddress );
    console.log("Verify the updated value that was set .. " )
    await getValueAtAddress(provider, contractAbi, contractAddress);
  })
  .catch(console.error);
}

if (require.main === module) {
  main();
}

module.exports = exports = main
