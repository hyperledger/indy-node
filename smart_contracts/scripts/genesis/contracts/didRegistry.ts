import { ContractConfig } from '../contractConfig'
import { config } from '../config'
import { buildSection } from '../helpers'

export interface DidsConfig extends ContractConfig {
  libraries: { [libraryName: string]: string }
  data: {
    dids: Array<{ id: string; data: any }>
  }
}

export function didRegistry() {
  const { name, address, description, libraries } = config.didRegistry
  const storage: any = {}
  return buildSection(name, address, description, storage, libraries)
}
