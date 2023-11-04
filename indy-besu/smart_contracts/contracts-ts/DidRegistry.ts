import {
  DidDocumentStorageStruct,
  DidDocumentStruct,
  ServiceStruct,
  VerificationMethodStruct,
  VerificationRelationshipStruct,
} from '../typechain-types/contracts/did/DidRegistry'
import { Contract } from '../utils/contract'

export type DidDocumentStorage = DidDocumentStorageStruct
export type DidDocument = DidDocumentStruct
export type VerificationMethod = VerificationMethodStruct
export type VerificationRelationship = VerificationRelationshipStruct
export type Service = ServiceStruct

export class DidRegistry extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000003333'

  constructor(sender?: any) {
    super(DidRegistry.name, sender)
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
      document: {
        context: didDocumentStorage.document.context.map((context: string) => context),
        id: didDocumentStorage.document.id,
        controller: didDocumentStorage.document.controller,
        verificationMethod: didDocumentStorage.document.verificationMethod.map(
          (verificationMethod: VerificationMethod) => DidRegistry.mapVerificationMethod(verificationMethod),
        ),
        authentication: didDocumentStorage.document.authentication.map((relationship: VerificationRelationship) =>
          DidRegistry.mapVerificationRelationship(relationship),
        ),
        assertionMethod: didDocumentStorage.document.assertionMethod.map((relationship: VerificationRelationship) =>
          DidRegistry.mapVerificationRelationship(relationship),
        ),
        capabilityInvocation: didDocumentStorage.document.capabilityInvocation.map(
          (relationship: VerificationRelationship) => DidRegistry.mapVerificationRelationship(relationship),
        ),
        capabilityDelegation: didDocumentStorage.document.capabilityDelegation.map(
          (relationship: VerificationRelationship) => DidRegistry.mapVerificationRelationship(relationship),
        ),
        keyAgreement: didDocumentStorage.document.keyAgreement.map((relationship: VerificationRelationship) =>
          DidRegistry.mapVerificationRelationship(relationship),
        ),
        service: didDocumentStorage.document.service.map((relationship: Service) =>
          DidRegistry.mapService(relationship),
        ),
        alsoKnownAs: didDocumentStorage.document.alsoKnownAs.map((alsoKnownAs: string) => alsoKnownAs),
      },
      metadata: {
        created: didDocumentStorage.metadata.created,
        updated: didDocumentStorage.metadata.updated,
        deactivated: didDocumentStorage.metadata.deactivated,
      },
    } as DidDocumentStorage
  }

  private static mapVerificationMethod(verificationMethod: VerificationMethod): VerificationMethod {
    return {
      id: verificationMethod.id,
      verificationMethodType: verificationMethod.verificationMethodType,
      controller: verificationMethod.controller,
      publicKeyJwk: verificationMethod.publicKeyJwk,
      publicKeyMultibase: verificationMethod.publicKeyMultibase,
    }
  }

  private static mapVerificationRelationship(relationship: VerificationRelationship): VerificationRelationship {
    return {
      id: relationship.id,
      verificationMethod: DidRegistry.mapVerificationMethod(relationship.verificationMethod),
    }
  }

  private static mapService(service: Service): Service {
    return {
      id: service.id,
      serviceType: service.serviceType,
      serviceEndpoint: service.serviceEndpoint,
      accept: service.accept.map((accept: string) => accept),
      routingKeys: service.routingKeys.map((routingKey: string) => routingKey),
    }
  }
}
