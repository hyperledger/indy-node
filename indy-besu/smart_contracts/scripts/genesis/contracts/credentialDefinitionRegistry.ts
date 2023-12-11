import { padLeft } from 'web3-utils'
import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection, slots } from '../helpers'

export interface CredentialDefinitionsConfig extends ContractConfig {
  data: {
    credentialDefinitions: Array<{ id: string; data: { name: string } }>
    universalDidResolverAddress: string
    schemaRegistryAddress: string
    upgradeControlAddress: string
  }
}

export function credentialDefinitionRegistry() {
  const { name, address, description, data } = config.credentialDefinitionRegistry
  const storage: any = {}

  // address of upgrade control contact stored in slot 0
  storage[slots['0']] = padLeft(data.upgradeControlAddress, 64)
  // address of DID registry contact stored in slot 1
  storage[slots['1']] = padLeft(data.universalDidResolverAddress, 64)
  // address of schema registry contact stored in slot 2
  storage[slots['2']] = padLeft(data.schemaRegistryAddress, 64)
  return buildProxySection(name, address, description, storage)
}
