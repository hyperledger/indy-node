import { Contract } from '../utils/contract'

export class EthereumCLRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000111111'

  constructor(sender?: any) {
    super(EthereumCLRegistry.name, sender)
  }

  public async createResource(id: string, resource: string) {
    const tx = await this.instance.createResource(id, resource)
    const result = await tx.wait()
    console.log(result)
    return result
  }
}
