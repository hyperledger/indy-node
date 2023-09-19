import { readFileSync } from 'fs-extra'
import { ethers } from 'hardhat'
import path from 'path'
import { host } from "../environment";
import { Signer } from "ethers";

export class Contract {
    protected readonly name: string
    protected readonly signer?: Signer
    public address?: string
    protected instance: any

    constructor(name: string, sender?: any, address?: string) {
        this.name = name
        this.address = address
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

    public getInstance() {
        const contractPath = path.resolve(__dirname, '../', `artifacts/contracts`, `${this.name}.sol/${this.name}.json`)
        const contractJson = JSON.parse(readFileSync(contractPath, 'utf8'))
        this.address = this.address || '0x0000000000000000000000000000000000001111'
        this.instance = new ethers.Contract(this.address, contractJson.abi, this.signer)
        return this
    }

    public connect(account: Signer) {
        this.instance = this.instance.connect(account)
        return this
    }
}

