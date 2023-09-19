import { ValidatorControl } from "../contracts-ts/ValidatorControl";
import environment from "../environment";

async function demo() {
    const sender = environment.accounts.account1
    const contract = new ValidatorControl(sender).getInstance()

    console.log('1. Get the lst of current validate nodes')
    const validators = await contract.getValidators()
    console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)
}

if (require.main === module) {
    demo()
}

module.exports = exports = demo
