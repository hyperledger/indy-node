import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildSection, slots } from '../helpers'

export interface CredentialDefinitionsConfig extends ContractConfig {
  data: {
    credentialDefinitions: Array<{ id: string; data: { name: string } }>
    didRegistryAddress: string
    schemaRegistryAddress: string
  }
}

export function credentialDefinitionRegistry() {
  const { name, address, description, data } = config.credentialDefinitionRegistry
  const storage: any = {}

  storage[slots['0']] = padLeft(data.didRegistryAddress, 64)
  storage[slots['1']] = padLeft(data.schemaRegistryAddress, 64)
  return buildSection(name, address, description, storage)
}
