import Web3 from "web3";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";
import { ethers } from "hardhat";

export const web3 = new Web3()

export enum ROLES {
    EMPTY,
    TRUSTEE,
    ENDORSER,
    STEWARD
}

export interface TestAccountDetails {
    account: HardhatEthersSigner,
    role: ROLES
}

export interface TestAccounts {
    deployer: TestAccountDetails,
    trustee: TestAccountDetails,
    endorser: TestAccountDetails,
    steward: TestAccountDetails,
    noRole: TestAccountDetails,
}

export async function getTestAccounts(): Promise<TestAccounts> {
    let [ deployer, trustee, endorser, steward, noRole ] = await ethers.getSigners()
    return {
        deployer: {account: deployer, role: ROLES.TRUSTEE},
        trustee: {account: trustee, role: ROLES.TRUSTEE},
        endorser: {account: endorser, role: ROLES.ENDORSER},
        steward: {account: steward, role: ROLES.STEWARD},
        noRole: {account: noRole, role: ROLES.EMPTY},
    }
}
