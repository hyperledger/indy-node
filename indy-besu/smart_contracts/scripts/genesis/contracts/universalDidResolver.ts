import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface UniversalDidResolverConfig extends ContractConfig {
  data: {
    didRegistryAddress: string
    etheriumDidRegistryAddress: string
    upgradeControlAddress: string
  }
}

export function universalDidResolver() {
  const { name, address, description, data } = config.universalDidResolver
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  // address of DID registry contact stored in slot 1
  storage[slots['1']] = padLeft(data.didRegistryAddress, 64)
  // address of etherium DID registry contact stored in slot 2
  storage[slots['2']] = padLeft(data.etheriumDidRegistryAddress, 64)
  return buildProxySection(name, address, description, storage)
}
