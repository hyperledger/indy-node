import { ethers } from 'hardhat'
import { host } from '../environment'
import { Signer } from 'ethers'

export class Contract {
    public address?: string

    protected readonly name: string
    protected readonly signer?: Signer
    protected instance: any

    constructor(name: string, sender?: any) {
        this.name = name
        if (sender) {
            const provider = new ethers.JsonRpcProvider(host)
            this.signer = new ethers.Wallet(sender.privateKey, provider)
        }
    }

    public async deploy(options?: { params?: any, libraries?: [Contract] }) {
        const { params, libraries } = options || {}

        const libraryObject = libraries?.reduce<{ [libraryName: string]: string }>((acc, library) => {
            acc[library.name] = library.address!
            return acc
          }, {})
        
        if (params) {
            this.instance = await ethers.deployContract(
                this.name, 
                params, 
                { signer: this.signer, libraries: libraryObject }
            )
        } else {
            this.instance = await ethers.deployContract(
                this.name, 
                { signer: this.signer, libraries: libraryObject }
            )
        }

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
