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
const contractBytecode = contractJson.evm.bytecode.object

async function createDid(host, deployedContractAbi, deployedContractAddress, did){
  const web3 = new Web3(host);
  const contractInstance = new web3.eth.Contract(deployedContractAbi, deployedContractAddress);
  await contractInstance.methods.createDid(did).call();
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
    data: "0x"+contractBytecode,
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
    didIndy2 = "did:indy2:123456";
    await createDid(host, contractAbi, tx.contractAddress,didIndy2);
  })
  .catch(console.error);
}

if (require.main === module) {
  main();
}

module.exports = exports = main