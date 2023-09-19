import { Contract } from '../utils/contract'
import { CredentialDefinitionRegistryInterface } from '../typechain-types/cl/CredentialDefinitionRegistryInterface'

export type CredentialDefinition = CredentialDefinitionRegistryInterface.CredentialDefinitionStruct

export class CredentialDefinitionRegistry extends Contract {
  constructor(sender?: any) {
    super(CredentialDefinitionRegistry.name, sender)
  }

  async create(id: string, credDef: CredentialDefinition) {
    const tx = await this.instance.create(id, credDef)
    return tx.wait()
  }

  async resolve(id: string): Promise<CredentialDefinition> {
    const credDef = await this.instance.resolve(id)
    return {
      name: credDef.name,
    }
  }
}
