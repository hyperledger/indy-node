import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface SchemasConfig extends ContractConfig {
  data: {
    schemas: Array<{ id: string; data: { name: string } }>
    universalDidResolverAddress: string
    upgradeControlAddress: string
  }
}

export function schemaRegistry() {
  const { name, address, description, data } = config.schemaRegistry
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  // address of DID resolver contact stored in slot 1
  storage[slots['1']] = padLeft(data.universalDidResolverAddress, 64)
  return buildProxySection(name, address, description, storage)
}
