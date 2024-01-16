import {
  CredentialDefinitionStruct,
  CredentialDefinitionWithMetadataStruct,
} from '../../typechain-types/contracts/cl/CredentialDefinitionRegistryInterface'

export type CredentialDefinition = CredentialDefinitionStruct
export type CredentialDefinitionWithMetadata = CredentialDefinitionWithMetadataStruct

export function mapCredentialDefinitionWithMetadata(data: CredentialDefinitionWithMetadata) {
  return {
    credDef: {
      id: data.credDef.id,
      issuerId: data.credDef.issuerId,
      schemaId: data.credDef.schemaId,
      credDefType: data.credDef.credDefType,
      tag: data.credDef.tag,
      value: data.credDef.value,
    },
    metadata: {
      created: data.metadata.created,
    },
  }
}
