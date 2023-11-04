import environment from '../environment'
import { ROLES } from '../contracts-ts'
import { Account } from '../utils'
import { Actor } from './utils/actor'

// Change it with the new node address!!
const nodeAddress = '0xdf2aa4dfb7be2d4de6f9b1a4574248502ea198b1'

async function getValidatorsForLastBLock() {
  const response = await fetch(environment.besu.rpcnode.url, {
    method: 'POST',
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'qbft_getValidatorsByBlockNumber',
      params: ['latest'],
      id: 1,
    }),
  })
  return await response.json()
}

async function demo() {
  const trustee = await new Actor(environment.accounts.account1).init()
  const steward = await new Actor().init()

  console.log('1. Get the lst of current validate nodes')
  let validators = await trustee.validatorControl.getValidators()
  console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)

  console.log('2. Get the list of validate for last block')
  let data = await getValidatorsForLastBLock()
  console.log(`Response: ${JSON.stringify(data, null, 2)}`)

  console.log('3. Assign Steward role to target account')
  await trustee.roleControl.assignRole(ROLES.STEWARD, steward.address)

  console.log('4. Add new validator node')
  const addValidatorReceipt = await steward.validatorControl.addValidator(nodeAddress)
  console.log(`Validator ${nodeAddress} added to the network -- ${JSON.stringify(addValidatorReceipt)}`)

  console.log('5. Get the lst of current validate nodes')
  validators = await steward.validatorControl.getValidators()
  console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)

  const newAccount = new Account()
  console.log('6. Assign Trustee role to new account to ensure that network works')
  const receipt2 = await trustee.roleControl.assignRole(ROLES.TRUSTEE, newAccount.address)
  console.log(`Role ${ROLES.TRUSTEE} assigned to account ${newAccount.address} -- ${JSON.stringify(receipt2)}`)

  console.log('7. Get role of target account')
  const newAccountAssignedRole = await trustee.roleControl.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountAssignedRole} role assigned`)

  console.log('8. Get the list of validate for last block')
  data = await getValidatorsForLastBLock()
  console.log(`Response: ${JSON.stringify(data, null, 2)}`)

  console.log('9. Remove the validator node')
  const removeValidatorReceipt = await steward.validatorControl.removeValidator(nodeAddress)
  console.log(`Validator ${nodeAddress} removed from the network -- ${JSON.stringify(addValidatorReceipt)}`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
