import { encodeBase58, Signer } from 'ethers';
import { ethers } from 'hardhat';
import { environment, host, web3 } from '../environment';
import { createBaseDidDocument } from './entity-factories';

export interface AccountInfo {
    address: string,
    privateKey: string,
}

export class Account {
    public address: string
    public privateKey: string
    public signer: Signer

    constructor(data?: AccountInfo) {
        const provider = new ethers.JsonRpcProvider(host)
        if (data) {
            this.signer = new ethers.Wallet(data.privateKey, provider)
            this.address = data.address
            this.privateKey = data.privateKey
        } else {
            const account = web3.eth.accounts.create()
            this.signer = new ethers.Wallet(account.privateKey, provider)
            this.address = account.address
            this.privateKey = account.privateKey
        }
    }

    public get did() {
        // TODO: The DID's method-specefic-id is not generated according to the specification.
        // It needs to be adjusted to match the specification: Base58(Truncate_msb(16(SHA256(publicKey))))
        const did = `did:${environment.did.method}:${environment.network.name}:${encodeBase58(this.address).substring(0, 22)}`
        console.log(did)
        return did
    }

    public get didEthr() {
        return `did:ethr:${this.address}`
    }

    public get didDocument() {
        return createBaseDidDocument(this.did)
    }
}
