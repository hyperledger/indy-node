import { Contract } from '../utils/contract'
import { mapSchemaWithMetadata, Schema, SchemaWithMetadata } from './types'

export class SchemaRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000005555'

  constructor(sender?: any) {
    super(SchemaRegistry.name, sender)
  }

  public async createSchema(data: Schema) {
    const tx = await this.instance.createSchema(data)
    return tx.wait()
  }

  public async resolveSchema(id: string): Promise<SchemaWithMetadata> {
    const result = await this.instance.resolveSchema(id)
    return mapSchemaWithMetadata(result)
  }
}
