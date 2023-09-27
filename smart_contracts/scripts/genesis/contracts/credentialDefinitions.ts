import { ContractConfig } from '../contractConfig'
import { config } from '../config'
import { buildSection } from '../helpers'

export interface CredentialDefinitionsConfig extends ContractConfig {
  data: {
    credentialDefinitions: Array<{ id: string; data: { name: string } }>
  }
}

export function credentialDefinitions() {
  const { name, address, description } = config.credentialDefinitions
  const storage: any = {}
  return buildSection(name, address, description, storage)
}
