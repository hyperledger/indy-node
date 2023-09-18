import { HardhatEthersSigner } from '@nomicfoundation/hardhat-ethers/signers'
import { expect } from 'chai'
import { ethers } from 'hardhat'
import Web3 from 'web3'
import { DidRegistry } from '../typechain-types'

export const web3 = new Web3()

export const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

export enum ROLES {
  EMPTY,
  TRUSTEE,
  ENDORSER,
  STEWARD,
}

export interface TestAccountDetails {
  account: HardhatEthersSigner
  role: ROLES
}

export interface TestAccounts {
  deployer: TestAccountDetails
  trustee: TestAccountDetails
  trustee2: TestAccountDetails
  trustee3: TestAccountDetails
  endorser: TestAccountDetails
  endorser2: TestAccountDetails
  endorser3: TestAccountDetails
  steward: TestAccountDetails
  steward2: TestAccountDetails
  steward3: TestAccountDetails
  noRole: TestAccountDetails
  noRole2: TestAccountDetails
  noRole3: TestAccountDetails
}

export async function getTestAccounts(roleControl: any): Promise<TestAccounts> {
  const [
    deployer,
    trustee,
    trustee2,
    trustee3,
    endorser,
    endorser2,
    endorser3,
    steward,
    steward2,
    steward3,
    noRole,
    noRole2,
    noRole3,
  ] = await ethers.getSigners()

  const testAccounts: TestAccounts = {
    deployer: { account: deployer, role: ROLES.TRUSTEE },
    trustee: { account: trustee, role: ROLES.TRUSTEE },
    trustee2: { account: trustee2, role: ROLES.TRUSTEE },
    trustee3: { account: trustee3, role: ROLES.TRUSTEE },
    endorser: { account: endorser, role: ROLES.ENDORSER },
    endorser2: { account: endorser2, role: ROLES.ENDORSER },
    endorser3: { account: endorser3, role: ROLES.ENDORSER },
    steward: { account: steward, role: ROLES.STEWARD },
    steward2: { account: steward2, role: ROLES.STEWARD },
    steward3: { account: steward3, role: ROLES.STEWARD },
    noRole: { account: noRole, role: ROLES.EMPTY },
    noRole2: { account: noRole2, role: ROLES.EMPTY },
    noRole3: { account: noRole3, role: ROLES.EMPTY },
  }
  for (const party of Object.values(testAccounts)) {
    if (party.role !== ROLES.EMPTY) {
      await roleControl.connect(deployer).assignRole(party.role, party.account)
    }
  }
  return testAccounts
}

export function createBaseDidDocument(did: string): DidRegistry.DidDocumentStruct {
  const verificationMethod: DidRegistry.VerificationMethodStruct = {
    id: `${did}#KEY-1`,
    verificationMethodType: 'Ed25519VerificationKey2018',
    controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
    publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
    publicKeyJwk: '',
  }

  const authentication: DidRegistry.VerificationRelationshipStruct = {
    id: `${did}#KEY-1`,
    verificationMethod: {
      id: '',
      verificationMethodType: '',
      controller: '',
      publicKeyMultibase: '',
      publicKeyJwk: '',
    },
  }

  const didDocument: DidRegistry.DidDocumentStruct = {
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

export function createFakeSignature(did: string): DidRegistry.SignatureStruct {
  return {
    id: did,
    value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd',
  }
}

export function assertDidDocument(
  actual: DidRegistry.DidDocumentStructOutput,
  expected: DidRegistry.DidDocumentStruct,
) {
  expect(actual.context).to.have.all.members(expected.context)
  expect(actual.id).to.equals(expected.id)
  expect(actual.controller).to.have.all.members(expected.controller)
  expect(actual.alsoKnownAs).to.have.all.members(expected.alsoKnownAs)

  assertArray(actual.verificationMethod, expected.verificationMethod, assetVerificationMethod)
  assertArray(actual.authentication, expected.authentication, assetVerificationRelationship)
  assertArray(actual.assertionMethod, expected.assertionMethod, assetVerificationRelationship)
  assertArray(actual.capabilityInvocation, expected.capabilityInvocation, assetVerificationRelationship)
  assertArray(actual.capabilityDelegation, expected.capabilityDelegation, assetVerificationRelationship)
  assertArray(actual.keyAgreement, expected.keyAgreement, assetVerificationRelationship)
  assertArray(actual.service, expected.service, assetService)
}

export function assetVerificationMethod(
  actual: DidRegistry.VerificationMethodStructOutput,
  expected: DidRegistry.VerificationMethodStruct,
) {
  expect(actual.id).to.equals(expected.id)
  expect(actual.verificationMethodType).to.equals(expected.verificationMethodType)
  expect(actual.controller).to.equals(expected.controller)
  expect(actual.publicKeyJwk).to.equals(expected.publicKeyJwk)
  expect(actual.publicKeyMultibase).to.equals(expected.publicKeyMultibase)
}

export function assetVerificationRelationship(
  actual: DidRegistry.VerificationRelationshipStructOutput,
  expected: DidRegistry.VerificationRelationshipStruct,
) {
  expect(actual.id).to.equals(expected.id)
  assetVerificationMethod(actual.verificationMethod, expected.verificationMethod)
}

export function assetService(actual: DidRegistry.ServiceStructOutput, expected: DidRegistry.ServiceStruct) {
  expect(actual.id).to.equals(expected.id)
  expect(actual.serviceType).to.equals(expected.serviceType)
  expect(actual.serviceEndpoint).to.have.all.members(expected.serviceEndpoint)
  expect(actual.accept).to.have.all.members(expected.accept)
  expect(actual.routingKeys).to.have.all.members(expected.routingKeys)
}

export function assertArray<A, E>(actualArray: A[], expectedArray: E[], fn: (actual: A, expected: E) => void) {
  expect(actualArray.length).to.equals(expectedArray.length)

  actualArray.every((element, index) => fn(element, expectedArray[index]))
}
