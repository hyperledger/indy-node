import { padLeft } from 'web3-utils'
import { config } from '../config'
import { buildSection, slots } from '../helpers'

export interface AccountControlConfig {
  name: string
  address: string
  description: string
  data: {
    roleControlContractAddress: string
  }
}

export function accountControl() {
  const { name, address, description, data } = config.accountControl
  const storage: any = {}

  storage[slots['0']] = padLeft(data.roleControlContractAddress, 64)
  return buildSection(name, address, description, storage)
}
