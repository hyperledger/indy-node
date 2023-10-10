import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildSection, slots } from '../helpers'

export interface SchemasConfig extends ContractConfig {
  data: {
    schemas: Array<{ id: string; data: { name: string } }>
    didRegistryAddress: string
  }
}

export function schemaRegistry() {
  const { name, address, description, data } = config.schemaRegistry
  const storage: any = {}

  storage[slots['0']] = padLeft(data.didRegistryAddress, 64)
  return buildSection(name, address, description, storage)
}
