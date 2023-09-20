import { readFileSync } from 'fs-extra'
import { ethers } from 'hardhat'
import { resolve } from 'path'
import { host } from "../environment";
import { Signer } from "ethers";

export class Contract {
    public address?: string

    protected readonly name: string
    protected readonly path: string
    protected readonly signer?: Signer
    protected instance: any

    constructor(name: string, path: string, sender?: any, address?: string) {
        this.name = name
        this.path = path
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
        const contractPath = resolve(__dirname, '../', `artifacts/contracts`, this.path, `${this.name}.sol/${this.name}.json`)
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

