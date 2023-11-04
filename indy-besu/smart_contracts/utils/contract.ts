import { Signer } from 'ethers';
import { ethers, upgrades } from 'hardhat'
import { host } from '../environment'

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

    public async deployProxy(options?: { params?: any, libraries?: [Contract] }) {
        const { params, libraries } = options || {}

        const factory = await ethers.getContractFactory(
            this.name,
            { signer: this.signer, libraries: this.toDictionary(libraries) },
        )

        this.instance = await upgrades.deployProxy(
            factory,
            params ?? [],
            { kind: 'uups', unsafeAllowLinkedLibraries: true }
        )
        await this.instance.waitForDeployment()

        this.address = await this.instance.getAddress()
        return this
    }

    public async deploy(options?: { params?: any, libraries?: [Contract] }) {
        const { params, libraries } = options || {}

        const libraryObject = libraries?.reduce<{ [libraryName: string]: string }>((acc, library) => {
            acc[library.name] = library.address!
            return acc
          }, {})

        this.instance = await ethers.deployContract(
            this.name,
            params ?? [],
            { signer: this.signer, libraries: libraryObject }
        )
        await this.instance.waitForDeployment()

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

    private toDictionary(libraries?: [Contract]) {
        return libraries?.reduce<{ [libraryName: string]: string }>((acc, library) => {
            acc[library.name] = library.address!
            return acc
          }, {})
    }
}
