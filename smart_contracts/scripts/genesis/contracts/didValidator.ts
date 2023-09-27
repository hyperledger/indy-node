import { ContractConfig } from '../contractConfig'
import { config } from '../config'
import { buildSection } from '../helpers'

export interface DidValidatorConfig extends ContractConfig {
  libraries: { [libraryName: string]: string }
}

export function didValidator() {
  const { name, address, description, libraries } = config.didValidator
  const storage: any = {}
  return buildSection(name, address, description, storage, libraries)
}
