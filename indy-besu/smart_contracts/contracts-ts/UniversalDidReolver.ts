import { Contract } from '../utils'
import { DidDocument, DidMetadata, mapDidDocument, mapDidMetadata } from './types'

export class UniversalDidResolver extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000003030'

  constructor(sender?: any) {
    super(UniversalDidResolver.name, sender)
  }

  public async resolveDocument(id: string): Promise<DidDocument> {
    const document = await this.instance.resolveDocument(id)
    return mapDidDocument(document)
  }

  public async resolveMetadata(id: string): Promise<DidMetadata> {
    const metadata = await this.instance.resolveMetadata(id)
    return mapDidMetadata(metadata)
  }
}
