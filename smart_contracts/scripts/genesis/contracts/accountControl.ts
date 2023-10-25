import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface AccountControlConfig extends ContractConfig {
  data: {
    roleControlContractAddress: string
    upgradeControlAddress: string
  }
}

export function accountControl() {
  const { name, address, description, data } = config.accountControl
  const storage: any = {}

  // address of upgrade control contact stored in slot 1
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  // address of role control contact stored in slot 0
  storage[slots['1']] = padLeft(data.roleControlContractAddress, 64)
  return buildProxySection(name, address, description, storage)
}
