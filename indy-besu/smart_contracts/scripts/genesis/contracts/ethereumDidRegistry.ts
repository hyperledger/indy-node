import { config } from '../config'
import { ContractConfig } from '../contractConfig'
import { buildProxySection } from '../helpers'

export interface EthereumDidRegistryConfig extends ContractConfig {}

export function ethereumDidRegistry() {
  const { name, address, description } = config.ethereumDidRegistry
  const storage: any = {}

  return buildProxySection(name, address, description, storage)
}
