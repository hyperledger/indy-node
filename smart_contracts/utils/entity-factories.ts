import { CredentialDefinition, DidDocument, Schema, VerificationMethod, VerificationRelationship } from '../contracts-ts'

export function createBaseDidDocument(did: string): DidDocument {
  const verificationMethod: VerificationMethod = {
    id: `${did}#KEY-1`,
    verificationMethodType: 'Ed25519VerificationKey2018',
    controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
    publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
    publicKeyJwk: '',
  }

  const authentication: VerificationRelationship = {
    id: `${did}#KEY-1`,
    verificationMethod: {
      id: '',
      verificationMethodType: '',
      controller: '',
      publicKeyMultibase: '',
      publicKeyJwk: '',
    },
  }

  const didDocument: DidDocument = {
    context: [],
    id: did,
    controller: [],
    verificationMethod: [verificationMethod],
    authentication: [authentication],
    assertionMethod: [],
    capabilityInvocation: [],
    capabilityDelegation: [],
    keyAgreement: [],
    service: [],
    alsoKnownAs: [],
  }

  return didDocument
}

interface CreateShemaParams {
  issuerId: string
  name?: string
  version?: string
  attrNames?: string[]
}

export function createSchemaObject({
  issuerId,
  name = 'BasicIdentity',
  version = '1.0.0',
  attrNames = ['First Name', 'Last Name'],
}: CreateShemaParams): Schema {
  return {
    id: `${issuerId}/anoncreds/v0/SCHEMA/${name}/${version}`,
    issuerId,
    name,
    version,
    attrNames,
  }
}

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