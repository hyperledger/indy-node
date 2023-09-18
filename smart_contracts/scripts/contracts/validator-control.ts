import { environment } from '../environment'
import { getContractInstance } from '../utils'

async function getValidators(contract: any) {
  const validators = await contract.getValidators()
  console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)
}

async function main() {
  const sender = environment.accounts.account1
  const contract = await getContractInstance(sender, environment.contracts.validatorControl)
  await getValidators(contract)
}

if (require.main === module) {
  main()
}

module.exports = exports = main
