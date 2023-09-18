import { readFileSync } from 'fs-extra'
import { ethers } from 'hardhat'
import path from 'path'
import { host } from "../environment";

export class Contract {
    public static deploy() {

    }

    public static getInstance(sender: any, name: any, address: string) {
        const contractPath = path.resolve(__dirname, '../', `artifacts/contracts`, `${name}.sol/${name}.json`)
        const contractJson = JSON.parse(readFileSync(contractPath, 'utf8'))

        const provider = new ethers.JsonRpcProvider(host)
        const signer = new ethers.Wallet(sender.privateKey, provider)

        return new ethers.Contract(address, contractJson.abi, signer)
    }
}

