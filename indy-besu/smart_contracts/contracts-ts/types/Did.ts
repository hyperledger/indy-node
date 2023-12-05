import {
  DidDocumentStorageStruct,
  DidDocumentStruct,
  DidMetadataStruct,
  ServiceStruct,
  VerificationMethodStruct,
  VerificationRelationshipStruct,
} from '../../typechain-types/contracts/did/DidRegistry'

export type DidDocumentStorage = DidDocumentStorageStruct
export type DidMetadata = DidMetadataStruct
export type DidDocument = DidDocumentStruct
export type VerificationMethod = VerificationMethodStruct
export type VerificationRelationship = VerificationRelationshipStruct
export type Service = ServiceStruct

export function mapDidDocument(document: DidDocument) {
  return {
    context: document.context.map((context: string) => context),
    id: document.id,
    controller: document.controller,
    verificationMethod: document.verificationMethod.map((verificationMethod: VerificationMethod) =>
      mapVerificationMethod(verificationMethod),
    ),
    authentication: document.authentication.map((relationship: VerificationRelationship) =>
      mapVerificationRelationship(relationship),
    ),
    assertionMethod: document.assertionMethod.map((relationship: VerificationRelationship) =>
      mapVerificationRelationship(relationship),
    ),
    capabilityInvocation: document.capabilityInvocation.map((relationship: VerificationRelationship) =>
      mapVerificationRelationship(relationship),
    ),
    capabilityDelegation: document.capabilityDelegation.map((relationship: VerificationRelationship) =>
      mapVerificationRelationship(relationship),
    ),
    keyAgreement: document.keyAgreement.map((relationship: VerificationRelationship) =>
      mapVerificationRelationship(relationship),
    ),
    service: document.service.map((relationship: Service) => mapService(relationship)),
    alsoKnownAs: document.alsoKnownAs.map((alsoKnownAs: string) => alsoKnownAs),
  }
}

export function mapDidMetadata(metadata: DidMetadata) {
  return {
    creator: metadata.creator,
    created: metadata.created,
    updated: metadata.updated,
    deactivated: metadata.deactivated,
  }
}

export function mapVerificationMethod(verificationMethod: VerificationMethod): VerificationMethod {
  return {
    id: verificationMethod.id,
    verificationMethodType: verificationMethod.verificationMethodType,
    controller: verificationMethod.controller,
    publicKeyJwk: verificationMethod.publicKeyJwk,
    publicKeyMultibase: verificationMethod.publicKeyMultibase,
  }
}

export function mapVerificationRelationship(relationship: VerificationRelationship): VerificationRelationship {
  return {
    id: relationship.id,
    verificationMethod: mapVerificationMethod(relationship.verificationMethod),
  }
}

export function mapService(service: Service): Service {
  return {
    id: service.id,
    serviceType: service.serviceType,
    serviceEndpoint: service.serviceEndpoint,
    accept: service.accept.map((accept: string) => accept),
    routingKeys: service.routingKeys.map((routingKey: string) => routingKey),
  }
}
