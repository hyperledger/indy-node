import { SchemaRegistryInterface } from '../typechain-types/cl/SchemaRegistryInterface'
import { Contract } from '../utils/contract'

export type Schema = SchemaRegistryInterface.SchemaStruct

export class SchemaRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000005555'

  constructor(sender?: any) {
    super(SchemaRegistry.name, sender)
  }

  public async create(id: string, schema: Schema) {
    const tx = await this.instance.create(id, schema)
    return tx.wait()
  }

  public async resolve(id: string): Promise<Schema> {
    const schema = await this.instance.resolve(id)
    return {
      name: schema.name,
    }
  }
}
