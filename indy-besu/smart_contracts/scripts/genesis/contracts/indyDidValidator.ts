import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildSection } from '../helpers'

export interface IndyDidValidatorConfig extends ContractConfig {}

export function indyDidValidator() {
  const { name, address, description } = config.indyDidValidator
  const storage: any = {}
  return buildSection(name, address, description, storage)
}
