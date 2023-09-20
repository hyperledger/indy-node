import { Contract } from '../utils/contract'

export class DidRegistry extends Contract {

  constructor(sender?: any, address?: string) {
    super(DidRegistry.name, 'did', sender, address)
  }

  async createDid(didDocument: any, signatures: Array<any>) {
    const tx = this.instance.createDid(didDocument, signatures)
    return tx.wait()
  }

  async updateDid(didDocument: any, signatures: Array<any>) {
    const tx = this.instance.updateDid(didDocument, signatures)
    return tx.wait()
  }

  async deactivateDid(id: string, signatures: Array<any>) {
    const tx = this.instance.deactivateDid(id, signatures)
    return tx.wait()
  }

  async resolve(id: string) {
    return this.instance.resolve(id)
  }

}
