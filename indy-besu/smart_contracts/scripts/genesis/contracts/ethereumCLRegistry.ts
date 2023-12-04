import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface EthereumCLRegistryConfig extends ContractConfig {
  data: {
    upgradeControlAddress: string
  }
}

export function ethereumCLRegistry() {
  const { name, address, description, data } = config.ethereumCLRegistry
  const storage: any = {}

  // address of upgrade control contact stored in slot 1
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  return buildProxySection(name, address, description, storage)
}
