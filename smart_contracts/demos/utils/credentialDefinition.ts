import { CredentialDefinition } from "../../contracts-ts"

interface CreateCredentialDefinitionParams {
  issuerId: string
  schemaId: string
  credDefType?: string
  tag?: string
  value?: string
}

export function createCredentialDefinitionObject({
  issuerId,
  schemaId,
  credDefType = 'CL',
  tag = 'BasicIdentity',
  value = '{ "n": "779...397", "rctxt": "774...977", "s": "750..893", "z": "632...005" }',
}: CreateCredentialDefinitionParams): CredentialDefinition {
  return {
    id: `${issuerId}/anoncreds/v0/CLAIM_DEF/${schemaId}/${tag}`,
    issuerId,
    schemaId,
    credDefType,
    tag,
    value,
  }
}
