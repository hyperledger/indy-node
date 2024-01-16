import { SchemaStruct, SchemaWithMetadataStruct } from '../../typechain-types/contracts/cl/SchemaRegistryInterface'

export type Schema = SchemaStruct
export type SchemaWithMetadata = SchemaWithMetadataStruct

export function mapSchemaWithMetadata(data: SchemaWithMetadata) {
  return {
    schema: {
      id: data.schema.id,
      issuerId: data.schema.issuerId,
      name: data.schema.name,
      version: data.schema.version,
      attrNames: data.schema.attrNames,
    },
    metadata: {
      created: data.metadata.created,
    },
  }
}
