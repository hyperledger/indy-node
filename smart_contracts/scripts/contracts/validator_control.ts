const {getContractInstance} = require("../environment");
const {environment} = require("../environment");

async function getValidators(contract: any) {
    const validators = await contract.methods.getValidators().call();
    console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)
}

async function main() {
    const contract = await getContractInstance(environment.contracts.roleControl)
    getValidators(contract).catch(console.error);
}

if (require.main === module) {
    main();
}

module.exports = exports = main
