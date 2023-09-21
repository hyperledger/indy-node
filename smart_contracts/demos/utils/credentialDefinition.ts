import { randomString } from '../../utils'

export class CredentialDefinition {
  public id: string
  public data: { name: string }

  constructor() {
    this.id = `did:2:${randomString()}:1.0`
    this.data = {
      name: randomString(),
    }
  }
}
