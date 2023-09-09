const path = require('path');
const fs = require('fs-extra');
var ethers = require('ethers');

// member1 details
const { accounts, besu } = require("../keys.js");
const host = besu.rpcnode.url;
// one of the seeded accounts
const accountAPrivateKey = accounts.a.privateKey;

async function main(){
  const provider = new ethers.JsonRpcProvider(host);

  const walletA = new ethers.Wallet(accountAPrivateKey, provider);
  var accountABalance = await provider.getBalance(walletA.address);
  console.log("Account A has balance of: " + accountABalance);

  // create a new account to use to transfer eth to
  const walletB = ethers.Wallet.createRandom()
  var accountBBalance = await provider.getBalance(walletB.address);
  console.log("Account B has balance of: " + accountBBalance);

  const nonce = await provider.getTransactionCount(walletA.address);
  const feeData = await provider.getFeeData();
  const gasLimit = await provider.estimateGas({from: walletA.address, value: ethers.parseEther("0.01")});

  // send some eth from A to B
  const txn = {
    nonce: nonce,
    from: walletA.address,
    to: walletB.address, 
    value: 0x10,  //amount of eth to transfer
    gasPrice: feeData.gasPrice, //ETH per unit of gas
    gasLimit: gasLimit //max number of gas units the tx is allowed to use
  };

  console.log("create and sign the txn")
  const signedTx = await walletA.sendTransaction(txn);
  await signedTx.wait();
  console.log("tx transactionHash: " + signedTx.hash);

  //After the transaction there should be some ETH transferred
  accountABalance = await provider.getBalance(walletA.address);
  console.log("Account A has balance of: " + accountABalance);
  accountBBalance = await provider.getBalance(walletB.address);
  console.log("Account B has balance of: " + accountBBalance);

}

if (require.main === module) {
  main();
}

module.exports = exports = main

