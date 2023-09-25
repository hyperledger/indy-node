import { padLeft, sha3 } from 'web3-utils'
import { config } from '../config'
import { buildSection, slots } from '../helpers'

export interface RolesConfig {
  name: string
  address: string
  description: string
  data: {
    accounts: Array<{ account: string; role: number }>
    roleOwners: Record<string, string>
  }
}

export function roles() {
  const { name, address, description, data } = config.roles
  const storage: any = {}

  // mappings for the account to role are stored in slot sha3(account | slot(0))
  for (const account of data.accounts) {
    const slot = sha3('0x' + padLeft(account.account.substring(2), 64) + slots['0'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(account.role.toString(16), 64)
  }

  // mappings for the account to role are stored in slot sha3(role | slot(1))
  for (const [role, owner] of Object.entries(data.roleOwners)) {
    const role_ = padLeft(parseInt(role, 10).toString(16), 64)
    const slot = sha3('0x' + role_ + slots['1'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(parseInt(owner, 10).toString(16), 64)
  }

  return buildSection(name, address, description, storage)
}
