import { web3 } from "../environment";
import { Account as Web3Account } from "web3-core";

export class Account {
    account: Web3Account

    constructor() {
        this.account = web3.eth.accounts.create()
    }

    public get address(){
        return this.account.address
    }
}
