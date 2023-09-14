import { ethers } from "hardhat";

const {getContractInstance} = require("../environment");
const {environment} = require("../environment");

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

async function getRole(contract: any, did: string) {
    const result = await contract.methods.getRole(did).call();
    console.log(`Account ${did} has ${result} role assigned`)
}

async function hasRole(contract: any, role: number, did: string) {
    const result = await contract.methods.hasRole(role, did).call();
    console.log(`Is account ${did} has ${role} role assigned? -- ${result}`)
}

async function getRoleOwner(contract: any, role: number) {
    const result = await contract.methods.getRoleOwner(role).call();
    console.log(`Role ${role} owned by ${result}`)
}

async function assignRole(contract: any, role: number, account: string) {
    const result = await contract.methods.assignRole(role, account).call();
    console.log(`Role ${role} assigned to account ${account} -- ${result}`)
}

async function getAllPastEvents(contract: any) {
    const events = await contract.getPastEvents("allEvents", {
        fromBlock: 0,
        toBlock: "latest",
    });
    console.log(
        "Obtained all value events from deployed contract : " + JSON.stringify(events)
    );
}

async function main() {
    const [ sender, account ] = await ethers.getSigners()
    const {contract} = await getContractInstance(environment.contracts.roleControl)

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

    await delay(5000)

    console.log('6. Get role of target account')
    await getRole(contract, account.address)

    console.log('7. Get all events from the contract')
    await getAllPastEvents(contract)
}

if (require.main === module) {
    main();
}

module.exports = exports = main
