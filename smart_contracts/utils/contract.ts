import { readFileSync } from 'fs-extra'
import { ethers } from 'hardhat'
import path from 'path'
import { host } from "../environment";

export class Contract {
    public static getInstance(sender: any, config: any) {
        const contractPath = path.resolve(__dirname, '../', 'contracts', config.spec)
        const contractJson = JSON.parse(readFileSync(contractPath, 'utf8'))

        const provider = new ethers.JsonRpcProvider(host)
        const signer = new ethers.Wallet(sender.privateKey, provider)

        return new ethers.Contract(config.address, contractJson.abi, signer)
    }
}

