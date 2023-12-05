import { Contract } from '../utils/contract'
import { CredentialDefinition, CredentialDefinitionWithMetadata, mapCredentialDefinitionWithMetadata } from './types'

export class CredentialDefinitionRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000004444'

  constructor(sender?: any) {
    super(CredentialDefinitionRegistry.name, sender)
  }

  public async createCredentialDefinition(credDef: CredentialDefinition) {
    const tx = await this.instance.createCredentialDefinition(credDef)
    return tx.wait()
  }

  public async resolveCredentialDefinition(id: string): Promise<CredentialDefinitionWithMetadata> {
    const result = await this.instance.resolveCredentialDefinition(id)
    return mapCredentialDefinitionWithMetadata(result)
  }
}
