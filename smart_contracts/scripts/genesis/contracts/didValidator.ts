import { config } from '../config'
import { buildSection } from '../helpers'

export interface DidValidatorConfig {
  name: string
  address: string
  description: string
}

export function didValidator() {
  const { name, address, description } = config.didValidator
  const storage: any = {}
  return buildSection(name, address, description, storage)
}
