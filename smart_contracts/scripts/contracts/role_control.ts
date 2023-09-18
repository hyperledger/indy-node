import { web3 } from '../environment'
import { environment } from '../environment'
import { getContractInstance } from '../utils'

async function getRole(contract: any, account: string) {
  const result = await contract.getRole(account)
  console.log(`Account ${account} has ${result} role assigned`)
}

async function hasRole(contract: any, role: number, did: string) {
  const result = await contract.hasRole(role, did)
  console.log(`Is account ${did} has ${role} role assigned? -- ${result}`)
}

async function getRoleOwner(contract: any, role: number) {
  const result = await contract.getRoleOwner(role)
  console.log(`Role ${role} owned by ${result}`)
}

async function assignRole(contract: any, role: number, account: string) {
  const tx = await contract.assignRole(role, account)
  const result = await tx.wait()
  console.log(`Role ${role} assigned to account ${account} -- ${JSON.stringify(result)}`)
}

async function revokeRole(contract: any, role: number, account: string) {
  const tx = await contract.revokeRole(role, account)
  const result = await tx.wait()
  console.log(`Role ${role} revoked from account ${account} -- ${JSON.stringify(result)}`)
}

async function main() {
  const sender = environment.accounts.account1
  const newAccount = web3.eth.accounts.create()
  const contract = await getContractInstance(sender, environment.contracts.roleControl)

  console.log('1. Get role for the current account')
  await getRole(contract, sender.address)

  console.log('2. Get role for the target account')
  await getRole(contract, newAccount.address)

  console.log('3. Check if target account has Trustee role assigned')
  await hasRole(contract, 1, newAccount.address)

  console.log('4. Get owner role of Trustee role')
  await getRoleOwner(contract, 1)

  console.log('6. Get role of target account')
  await getRole(contract, newAccount.address)

  console.log('5. Assign Trustee role to target account')
  await assignRole(contract, 1, newAccount.address)

  console.log('6. Get role of target account')
  await getRole(contract, newAccount.address)

  console.log('7. Revoke Trustee role from target account')
  await revokeRole(contract, 1, newAccount.address)

  console.log('8. Get role of target account')
  await getRole(contract, newAccount.address)
}

if (require.main === module) {
  main()
}

module.exports = exports = main
