import { padLeft, sha3, toHex } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface RolesConfig extends ContractConfig {
  data: {
    accounts: Array<{ account: string; role: number }>
    roleOwners: Record<string, string>
    upgradeControlAddress: string
  }
}

export function roleControl() {
  const { name, address, description, data } = config.roleControl
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)

  // mappings for the account to role are stored in slot sha3(account | slot(1))
  for (const account of data.accounts) {
    const slot = sha3('0x' + padLeft(account.account.substring(2), 64) + slots['1'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(account.role.toString(16), 64)
  }

  // mappings for the account to role are stored in slot sha3(role | slot(2))
  for (const [role, owner] of Object.entries(data.roleOwners)) {
    const role_ = padLeft(parseInt(role, 10).toString(16), 64)
    const slot = sha3('0x' + role_ + slots['2'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(parseInt(owner, 10).toString(16), 64)
  }

  // Group account based on their role and compute a count
  const roleCounts = data.accounts.reduce<Record<string, number>>((previous, current) => {
    let count = previous[current.role] || 0
    previous[current.role] = ++count
    return previous
  }, {})

  // mappings for the roles to their count are stored in slot sha3(role | slot(3))
  Object.entries(roleCounts).forEach(([role, count]) => {
    const role_ = padLeft(parseInt(role, 10).toString(16), 64)
    const slot = sha3('0x' + role_ + slots['3'])!
      .substring(2)
      .toLowerCase()
    storage[padLeft(slot, 64)] = padLeft(toHex(count), 64).substring(2)
  })

  return buildProxySection(name, address, description, storage)
}
