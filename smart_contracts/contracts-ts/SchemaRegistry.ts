import { Contract } from '../utils/contract'
import { SchemaRegistryInterface } from '../typechain-types/cl/SchemaRegistryInterface'

export type Schema = SchemaRegistryInterface.SchemaStruct

export class SchemaRegistry extends Contract {
  constructor(sender?: any) {
    super(SchemaRegistry.name, sender)
  }

  async create(id: string, schema: Schema) {
    const tx = await this.instance.create(id, schema)
    return tx.wait()
  }

  async resolve(id: string): Promise<Schema> {
    const schema = await this.instance.resolve(id)
    return {
      name: schema.name,
    }
  }
}
