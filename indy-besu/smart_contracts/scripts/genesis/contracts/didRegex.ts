import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildSection } from '../helpers'

export interface DidRegexConfig extends ContractConfig {}

export function didRegex() {
  const { name, address, description } = config.didRegex
  const storage: any = {}
  return buildSection(name, address, description, storage)
}
