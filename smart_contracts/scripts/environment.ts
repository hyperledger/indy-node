import { ethers } from "hardhat";

const path = require('path');
const fs = require('fs-extra');
const Web3 = require('web3');

const { besu } = require("./keys.ts");

export const web3 = new Web3(besu.rpcnode.url);

export const environment = {
  contracts: {
    roleControl: {
      spec: 'RoleControl.json',
      address: '0x0000000000000000000000000000000000006666',
    },
    validatorControl: {
      spec: 'ValidatorsControl.json',
      address: '0x0000000000000000000000000000000000007777',
    }
  }
}

export async function getContractInstance( config: any ) {
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
  const contractPath = path.resolve(__dirname, '../', 'contracts', config.spec)
  const contractJson = JSON.parse(fs.readFileSync(contractPath));
  const [ sender ] = await ethers.getSigners()

  // way 1
  // const mycontract = await new web3.eth.Contract(contractJson.abi, config.address);

  // way 2
  // const factory = new ethers.ContractFactory(contractJson.abi, contractJson.evm.bytecode.object, sender);
  // return await factory.deploy();
  return   new ethers.Contract(config.address, contractJson.abi, provider);
}

export default environment
