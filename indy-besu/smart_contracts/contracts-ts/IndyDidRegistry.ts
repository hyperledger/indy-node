import { Contract } from '../utils/contract'
import { DidDocument, DidDocumentStorage, mapDidDocument, mapDidMetadata } from './types'

export class IndyDidRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000003333'

  constructor(sender?: any) {
    super(IndyDidRegistry.name, sender)
  }

  public async createDid(didDocument: DidDocument) {
    const tx = await this.instance.createDid(didDocument)
    return tx.wait()
  }

  public async updateDid(didDocument: DidDocument) {
    const tx = await this.instance.updateDid(didDocument)
    return tx.wait()
  }

  public async deactivateDid(id: string) {
    const tx = await this.instance.deactivateDid(id)
    return tx.wait()
  }

  public async resolveDid(id: string): Promise<DidDocumentStorage> {
    const didDocumentStorage = await this.instance.resolveDid(id)
    return {
      document: mapDidDocument(didDocumentStorage.document),
      metadata: mapDidMetadata(didDocumentStorage.metadata),
    }
  }
}
