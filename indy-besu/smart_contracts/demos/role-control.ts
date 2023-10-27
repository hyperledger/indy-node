import { ROLES } from '../contracts-ts'
import environment from '../environment'
import { Actor } from './utils/actor'

async function demo() {
  const trustee = await new Actor(environment.accounts.account1).init()
  const newAccount = await new Actor().init()

  console.log('1. Get role for the current account')
  const senderRole = await trustee.roleControl.getRole(newAccount.address)
  console.log(`Account ${trustee.address} has ${senderRole} role assigned`)

  console.log('2. Get role for the new account')
  const newAccountRole = await trustee.roleControl.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountRole} role assigned`)

  console.log('3. Check if target account has Trustee role assigned')
  const hasRole = await trustee.roleControl.hasRole(1, newAccount.address)
  console.log(`Is account ${newAccount.address} has ${ROLES.TRUSTEE} role assigned? -- ${hasRole}`)

  console.log('4. Assign Trustee role to target account')
  let receipt = await trustee.roleControl.assignRole(ROLES.TRUSTEE, newAccount.address)
  console.log(`Role ${ROLES.TRUSTEE} assigned to account ${newAccount.address} -- ${JSON.stringify(receipt)}`)

  console.log('5. Get role of target account')
  let newAccountAssignedRole = await trustee.roleControl.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountAssignedRole} role assigned`)

  const newAccount2 = await new Actor().init()
  console.log('6. New Trustee account Assign Endorser role to second new account')
  receipt = await newAccount.roleControl.assignRole(ROLES.TRUSTEE, newAccount2.address)
  console.log(`Role ${ROLES.TRUSTEE} assigned to account ${newAccount2.address} -- ${JSON.stringify(receipt)}`)

  console.log('7. Get role of the second account')
  newAccountAssignedRole = await newAccount2.roleControl.getRole(newAccount2.address)
  console.log(`Account ${newAccount.address} has ${newAccountAssignedRole} role assigned`)

  console.log('8. Revoke Trustee role from target account')
  receipt = await trustee.roleControl.revokeRole(ROLES.TRUSTEE, newAccount.address)
  console.log(`Role ${ROLES.TRUSTEE} revoked from account ${newAccount.address} -- ${JSON.stringify(receipt)}`)

  console.log('9. Get role of target account')
  const newAccountRevokeRole = await trustee.roleControl.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountRevokeRole} role assigned`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
