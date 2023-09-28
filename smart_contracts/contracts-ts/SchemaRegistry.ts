import { SchemaDataStruct, SchemaStruct } from '../typechain-types/cl/SchemaRegistryInterface'
import { Contract } from '../utils/contract'

export type Schema = SchemaStruct
export type SchemaData = SchemaDataStruct

export class SchemaRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000005555'

  constructor(sender?: any) {
    super(SchemaRegistry.name, sender)
  }

  public async createSchema(data: SchemaData) {
    const tx = await this.instance.createSchema(data)
    return tx.wait()
  }

  public async resolveSchema(id: string): Promise<Schema> {
    const schema = await this.instance.resolveSchema(id)
    return {
      data: {
        id: schema.data.id,
        issuerId: schema.data.issuerId,
        name: schema.data.name,
        version: schema.data.version,
        attrNames: schema.data.attrNames,
      },
      metadata: {
        created: schema.created,
      },
    }
  }
}
