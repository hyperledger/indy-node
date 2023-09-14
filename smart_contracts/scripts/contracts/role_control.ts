import { ethers } from "hardhat";

const {getContractInstance} = require("../environment");
const {environment} = require("../environment");

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))


async function getRole(contract: any, account: string) {
    const [ sender ] = await ethers.getSigners()
    const result = await contract.getRole(account);
    console.log(`Account ${account} has ${result} role assigned`)
}

async function hasRole(contract: any, role: number, did: string) {
    const [ sender ] = await ethers.getSigners()
    const result = await contract.hasRole(role, did);
    console.log(`Is account ${did} has ${role} role assigned? -- ${result}`)
}

async function getRoleOwner(contract: any, role: number) {
    const [ sender ] = await ethers.getSigners()
    const result = await contract.getRoleOwner(role);
    console.log(`Role ${role} owned by ${result}`)
}

async function assignRole(contract: any, role: number, account: string) {
    const [ sender ] = await ethers.getSigners()
    const tx = await contract.connect(sender).assignRole(role, account)
    const result = await tx.wait();
    console.log(`Role ${role} assigned to account ${account} -- ${JSON.stringify(result)}`)
}

async function revokeRole(contract: any, role: number, account: string) {
    const [ sender ] = await ethers.getSigners()
    const tx = await contract.connect(sender).revokeRole(role, account)
    const result = await tx.wait();
    console.log(`Role ${role} revoked from account ${account} -- ${JSON.stringify(result)}`)
}

async function main() {
    const [ sender, account ] = await ethers.getSigners()

    const contract = await getContractInstance(environment.contracts.roleControl)

    console.log('1. Get role for the current account')
    await getRole(contract, sender.address);

    console.log('2. Get role for the target account')
    await getRole(contract, account.address);

    console.log('3. Check if target account has Trustee role assigned')
    await hasRole(contract, 1, account.address);

    console.log('4. Get owner role of Trustee role')
    await getRoleOwner(contract, 1);

    console.log('5. Assign Trustee role to target account')
    await assignRole(contract, 1, account.address);

    console.log('6. Get role of target account')
    await getRole(contract, account.address)

    console.log('6. Get role of target account')
    await getRole(contract, account.address)

    console.log('5. Assign Trustee role to target account')
    await revokeRole(contract, 1, account.address);

    console.log('6. Get role of target account')
    await getRole(contract, account.address)
}

if (require.main === module) {
    main();
}

module.exports = exports = main
