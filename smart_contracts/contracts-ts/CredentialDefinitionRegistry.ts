import { CredentialDefinitionRegistryInterface } from '../typechain-types/cl/CredentialDefinitionRegistryInterface'
import { Contract } from '../utils/contract'

export type CredentialDefinition = CredentialDefinitionRegistryInterface.CredentialDefinitionStruct

export class CredentialDefinitionRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000004444'

  constructor(sender?: any) {
    super(CredentialDefinitionRegistry.name, sender)
  }

  public async createCredentialDefinition(id: string, credDef: CredentialDefinition) {
    const tx = await this.instance.createCredentialDefinition(id, credDef)
    return tx.wait()
  }

  public async resolveCredentialDefinition(id: string): Promise<CredentialDefinition> {
    const credDef = await this.instance.resolveCredentialDefinition(id)
    return {
      name: credDef.name,
    }
  }
}
