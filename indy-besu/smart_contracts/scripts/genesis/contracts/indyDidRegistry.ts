import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface IndyDidRegistryConfig extends ContractConfig {
  libraries: { [libraryName: string]: string }
  data: {
    dids: Array<{ id: string; data: any }>
    upgradeControlAddress: string
  }
}

export function indyDidRegistry() {
  const { name, address, description, libraries, data } = config.indyDidRegistry
  const storage: any = {}

  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  return buildProxySection(name, address, description, storage, libraries)
}
