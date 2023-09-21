import { ethers } from 'hardhat'
import { host } from "../environment";
import { Signer } from "ethers";
import { Account } from "./account";

export class Contract {
    public address?: string

    protected readonly name: string
    protected readonly signer?: Signer
    protected instance: any

    constructor(name: string, sender?: Account) {
        this.name = name
        if (sender) {
            const provider = new ethers.JsonRpcProvider(host)
            this.signer = new ethers.Wallet(sender.privateKey, provider)
        }
    }

    public async deploy(params?: any) {
        this.instance = await ethers.deployContract(this.name, params, this.signer)
        this.address = await this.instance.getAddress()
        return this
    }

    public async getInstance(address: string) {
        this.instance = await ethers.getContractAt(this.name, address, this.signer)
        this.address = address
        return this
    }

    public connect(account: Signer) {
        this.instance = this.instance.connect(account)
        return this
    }
}

