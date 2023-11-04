import { SchemaStruct, SchemaWithMetadataStruct } from '../typechain-types/contracts/cl/SchemaRegistryInterface'
import { Contract } from '../utils/contract'

export type Schema = SchemaStruct
export type SchemaWithMetadata = SchemaWithMetadataStruct

export class SchemaRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000005555'

  constructor(sender?: any) {
    super(SchemaRegistry.name, sender)
  }

  public async createSchema(data: Schema) {
    const tx = await this.instance.createSchema(data)
    return tx.wait()
  }

  public async resolveSchema(id: string): Promise<SchemaWithMetadataStruct> {
    const result = await this.instance.resolveSchema(id)
    return {
      schema: {
        id: result.schema.id,
        issuerId: result.schema.issuerId,
        name: result.schema.name,
        version: result.schema.version,
        attrNames: result.schema.attrNames,
      },
      metadata: {
        created: result.metadata.created,
      },
    }
  }
}
