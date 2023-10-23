import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface UpgradeControlConfig extends ContractConfig {
  data: {
    roleControlContractAddress: string
  }
}

export function upgradeControl() {
  const { name, address, description, data } = config.upgradeControl
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.roleControlContractAddress, 64)
  return buildProxySection(name, address, description, storage)
}
