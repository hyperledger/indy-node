import { config } from '../config'
import { buildSection } from '../helpers'

export interface DidsConfig {
  name: string
  address: string
  description: string
  libraries: { [libraryName: string]: string }
  data: {
    dids: Array<{ id: string; data: any }>
  }
}

export function dids() {
  const { name, address, description, libraries } = config.dids
  const storage: any = {}
  return buildSection(name, address, description, storage, libraries)
}
