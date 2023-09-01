const path = require('path');
const fs = require('fs-extra');
const Web3 = require('web3');

// rpcnode details
const { tessera, besu } = require("../keys.js");
const host = besu.rpcnode.url;
const accountAddress = besu.rpcnode.accountAddress;

// abi and bytecode generated from simplestorage.sol:
// > solcjs --bin --abi simplestorage.sol
const contractJsonPath = path.resolve(__dirname, '../../','contracts','DidRegistry.json');
const contractJson = JSON.parse(fs.readFileSync(contractJsonPath));
const contractAbi = contractJson.abi;
const contractBytecode = "608060405234801561000f575f80fd5b506103f88061001d5f395ff3fe608060405234801561000f575f80fd5b5060043610610034575f3560e01c80633457d3e214610038578063e6fcc84b14610054575b5f80fd5b610052600480360381019061004d9190610284565b610072565b005b61005c6100ac565b6040516100699190610345565b60405180910390f35b7fbc8bea04588d600acc17fdb020b7541c88a62116ec5a7a961206cd709c3fcd06816040516100a19190610345565b60405180910390a150565b5f80546100b890610392565b80601f01602080910402602001604051908101604052809291908181526020018280546100e490610392565b801561012f5780601f106101065761010080835404028352916020019161012f565b820191905f5260205f20905b81548152906001019060200180831161011257829003601f168201915b505050505081565b5f604051905090565b5f80fd5b5f80fd5b5f80fd5b5f80fd5b5f601f19601f8301169050919050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52604160045260245ffd5b61019682610150565b810181811067ffffffffffffffff821117156101b5576101b4610160565b5b80604052505050565b5f6101c7610137565b90506101d3828261018d565b919050565b5f67ffffffffffffffff8211156101f2576101f1610160565b5b6101fb82610150565b9050602081019050919050565b828183375f83830152505050565b5f610228610223846101d8565b6101be565b9050828152602081018484840111156102445761024361014c565b5b61024f848285610208565b509392505050565b5f82601f83011261026b5761026a610148565b5b813561027b848260208601610216565b91505092915050565b5f6020828403121561029957610298610140565b5b5f82013567ffffffffffffffff8111156102b6576102b5610144565b5b6102c284828501610257565b91505092915050565b5f81519050919050565b5f82825260208201905092915050565b5f5b838110156103025780820151818401526020810190506102e7565b5f8484015250505050565b5f610317826102cb565b61032181856102d5565b93506103318185602086016102e5565b61033a81610150565b840191505092915050565b5f6020820190508181035f83015261035d818461030d565b905092915050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52602260045260245ffd5b5f60028204905060018216806103a957607f821691505b6020821081036103bc576103bb610365565b5b5091905056fea2646970667358221220821d0189fbfe4cd9bc0c6ba98c09393a6102a845987aa92a351c1b20ddb9e5e764736f6c63430008150033"
// initialize the default constructor with a value `47 = 0x2F`; this value is appended to the bytecode
const contractConstructorInit = "000000000000000000000000000000000000000000000000000000000000002F";
const contractConstructorUpdate = "000000000000000000000000000000000000000000000000000000000000001F";


async function getValueAtAddress(host, deployedContractAbi, deployedContractAddress){
  const web3 = new Web3(host);
  const contractInstance = new web3.eth.Contract(deployedContractAbi, deployedContractAddress);
  const res = await contractInstance.methods.get().call();
  console.log("Obtained value at deployed contract is: "+ res);
  return res
}

async function getAllPastEvents(host, deployedContractAbi, deployedContractAddress){
  const web3 = new Web3(host);
  const contractInstance = new web3.eth.Contract(deployedContractAbi, deployedContractAddress);
  const res = await contractInstance.getPastEvents("allEvents", {
    fromBlock: 0,
    toBlock: 'latest'
  })
  const amounts = res.map(x => {
    return x.returnValues._amount
  });
  console.log("Obtained all value events from deployed contract : [" + amounts + "]");
  return res
}

// You need to use the accountAddress details provided to Quorum to send/interact with contracts
async function setValueAtAddress(host, accountAddress, value, deployedContractAbi, deployedContractAddress){
  const web3 = new Web3(host);
  const account = web3.eth.accounts.create();
  // console.log(account);
  const contract = new web3.eth.Contract(deployedContractAbi);
  // eslint-disable-next-line no-underscore-dangle
  const functionAbi = contract._jsonInterface.find(e => {
    return e.name === "set";
  });
  const functionArgs = web3.eth.abi
    .encodeParameters(functionAbi.inputs, [value])
    .slice(2);
  const functionParams = {
    to: deployedContractAddress,
    data: functionAbi.signature + functionArgs,
    gas: "0x2CA51"  //max number of gas units the tx is allowed to use
  };
  const signedTx = await web3.eth.accounts.signTransaction(functionParams, account.privateKey);
   console.log("sending the txn")
  const txReceipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
  console.log("tx transactionHash: " + txReceipt.transactionHash);
  console.log("tx contractAddress: " + txReceipt.contractAddress);
  return txReceipt
}

async function createContract(host) {
  const web3 = new Web3(host);
  // make an account and sign the transaction with the account's private key; you can alternatively use an exsiting account
  const account = web3.eth.accounts.create();
  console.log(account);

  const txn = {
    chainId: 1337,
    nonce: await web3.eth.getTransactionCount(account.address),       // 0x00 because this is a new account
    from: account.address,
    to: null,            //public tx
    value: "0x00",
    data: '0x'+contractBytecode+contractConstructorInit,
    gasPrice: "0x0",     //ETH per unit of gas
    gas: "0x2CA51"  //max number of gas units the tx is allowed to use
  };

  console.log("create and sign the txn")
  const signedTx = await web3.eth.accounts.signTransaction(txn, account.privateKey);
  console.log("sending the txn")
  const txReceipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
  console.log("tx transactionHash: " + txReceipt.transactionHash);
  console.log("tx contractAddress: " + txReceipt.contractAddress);
  return txReceipt;
};

async function main(){
  createContract(host)
  .then(async function(tx){
    console.log("Contract deployed at address: " + tx.contractAddress);
    console.log("Use the smart contracts 'get' function to read the contract's constructor initialized value .. " )
    await getValueAtAddress(host, contractAbi, tx.contractAddress);
    console.log("Use the smart contracts 'set' function to update that value to 123 .. " );
    await setValueAtAddress(host, accountAddress, 123, contractAbi, tx.contractAddress );
    console.log("Verify the updated value that was set .. " )
    await getValueAtAddress(host, contractAbi, tx.contractAddress);
    await getAllPastEvents(host, contractAbi, tx.contractAddress);
  })
  .catch(console.error);
}

if (require.main === module) {
  main();
}

module.exports = exports = main