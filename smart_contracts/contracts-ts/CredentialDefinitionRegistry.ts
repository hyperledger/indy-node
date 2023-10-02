import { CredentialDefinitionStruct, CredentialDefinitionWithMetadataStruct } from '../typechain-types/cl/CredentialDefinitionRegistryInterface'
import { Contract } from '../utils/contract'

export type CredentialDefinition = CredentialDefinitionStruct
export type CredentialDefinitionWithMetadata = CredentialDefinitionWithMetadataStruct

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
    return {
      credDef: {
        id: result.credDef.id,
        issuerId: result.credDef.issuerId,
        schemaId: result.credDef.schemaId,
        entityType: result.credDef.entityType,
        tag: result.credDef.tag,
        value: result.credDef.value,
      },
      metadata: {
        created: result.metadata.create,
      },
    }
  }
}
