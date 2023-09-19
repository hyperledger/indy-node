import { Account } from '../utils/account'
import { RoleControl, ROLES } from '../contracts-ts/RoleControl'
import environment from '../environment'

async function demo() {
  const sender = environment.accounts.account1
  const newAccount = new Account()

  const contract = await new RoleControl(sender).getInstance(RoleControl.defaultAddress)

  console.log('1. Get role for the current account')
  const senderRole = await contract.getRole(sender.address)
  console.log(`Account ${sender.address} has ${senderRole} role assigned`)

  console.log('2. Get role for the new account')
  const newAccountRole = await contract.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountRole} role assigned`)

  console.log('3. Check if target account has Trustee role assigned')
  const hasRole = await contract.hasRole(1, newAccount.address)
  console.log(`Is account ${newAccount.address} has ${ROLES.TRUSTEE} role assigned? -- ${hasRole}`)

  console.log('4. Assign Trustee role to target account')
  const receipt = await contract.assignRole(ROLES.TRUSTEE, newAccount.address)
  console.log(`Role ${ROLES.TRUSTEE} assigned to account ${newAccount.address} -- ${JSON.stringify(receipt)}`)

  console.log('5. Get role of target account')
  const newAccountAssignedRole = await contract.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountAssignedRole} role assigned`)

  console.log('6. Revoke Trustee role from target account')
  const receipt2 = await contract.revokeRole(ROLES.TRUSTEE, newAccount.address)
  console.log(`Role ${ROLES.TRUSTEE} revoked from account ${newAccount.address} -- ${JSON.stringify(receipt2)}`)

  console.log('7. Get role of target account')
  const newAccountRevokeRole = await contract.getRole(newAccount.address)
  console.log(`Account ${newAccount.address} has ${newAccountRevokeRole} role assigned`)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
