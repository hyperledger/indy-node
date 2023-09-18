import { environment } from '../../environment'
import { Contract } from '../../utils/contract'
import { Account } from '../../utils/account'

export class RoleControl {
  private readonly name = 'RoleControl'
  private readonly address = '0x0000000000000000000000000000000000006666'
  private instance: any

  constructor(sender: any, address?: string) {
    this.instance = Contract.getInstance(sender, this.name, address || this.address)
  }

  async getRole(account: string) {
    const result = await this.instance.getRole(account)
    console.log(`Account ${account} has ${result} role assigned`)
  }

  async hasRole(role: number, did: string) {
    const result = await this.instance.hasRole(role, did)
    console.log(`Is account ${did} has ${role} role assigned? -- ${result}`)
  }

  async getRoleOwner(role: number) {
    const result = await this.instance.getRoleOwner(role)
    console.log(`Role ${role} owned by ${result}`)
  }

  async assignRole(role: number, account: string) {
    const tx = await this.instance.assignRole(role, account)
    const result = await tx.wait()
    console.log(`Role ${role} assigned to account ${account} -- ${JSON.stringify(result)}`)
  }

  async revokeRole(role: number, account: string) {
    const tx = await this.instance.revokeRole(role, account)
    const result = await tx.wait()
    console.log(`Role ${role} revoked from account ${account} -- ${JSON.stringify(result)}`)
  }
}

async function demo() {
  const sender = environment.accounts.account1
  const newAccount = new Account()

  const contract = new RoleControl(sender)

  console.log('1. Get role for the current account')
  await contract.getRole(sender.address)

  console.log('2. Get role for the target account')
  await contract.getRole(newAccount.address)

  console.log('3. Check if target account has Trustee role assigned')
  await contract.hasRole(1, newAccount.address)

  console.log('4. Get owner role of Trustee role')
  await contract.getRoleOwner(1)

  console.log('6. Get role of target account')
  await contract.getRole(newAccount.address)

  console.log('5. Assign Trustee role to target account')
  await contract.assignRole(1, newAccount.address)

  console.log('6. Get role of target account')
  await contract.getRole(newAccount.address)

  console.log('7. Revoke Trustee role from target account')
  await contract.revokeRole(1, newAccount.address)

  console.log('8. Get role of target account')
  await contract.getRole(newAccount.address)
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
