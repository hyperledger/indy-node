import { ethers } from 'ethers'
import { Contract } from '../../../utils'
import simpleContractJson from './simple-contract.json'

export class SimpleContract extends Contract {
  constructor(sender?: any) {
    super(SimpleContract.name, sender)
  }

  public async message() {
    return this.instance.message()
  }

  public async update(message: string) {
    let tx = await this.instance.update(message)
    return tx.wait()
  }

  public override async deploy(options?: { params?: any, libraries?: [Contract] }) {
    let factory = new ethers.ContractFactory(simpleContractJson.abi, simpleContractJson.bytecode, this.signer)

    const contract = await factory.deploy()
    this.address = await contract.getAddress()
    this.instance = contract

    return this
  }
}
