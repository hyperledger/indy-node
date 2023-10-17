import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildSection, slots } from '../helpers'

export interface UpgradeControlConfig extends ContractConfig {
  data: {
    roleControlContractAddress: string
  }
}

export function upgradeControl() {
  const { name, address, description, data } = config.upgradeControl
  const storage: any = {}

  storage[slots['0']] = padLeft(data.roleControlContractAddress, 64)
  return buildSection(name, address, description, storage)
}
