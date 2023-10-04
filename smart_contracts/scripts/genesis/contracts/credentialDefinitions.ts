import { padLeft } from 'web3-utils'
import { config } from '../config'
import { buildSection, slots } from '../helpers'

export interface CredentialDefinitionsConfig {
  name: string
  address: string
  description: string
  data: {
    credentialDefinitions: Array<{ id: string; data: { name: string } }>
    didRegistryAddress: string
    schemaRegistryAddress: string
  }
}

export function credentialDefinitions() {
  const { name, address, description, data } = config.credentialDefinitions
  const storage: any = {}

  storage[slots['0']] = padLeft(data.didRegistryAddress, 64)
  storage[slots['1']] = padLeft(data.schemaRegistryAddress, 64)
  return buildSection(name, address, description, storage)
}
