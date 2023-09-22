import { HardhatEthersSigner } from '@nomicfoundation/hardhat-ethers/signers'
import { ethers } from 'hardhat'
import { ROLES } from '../contracts-ts/RoleControl'
import { DidDocument, Signature, VerificationMethod, VerificationRelationship } from '../contracts-ts/DidRegistry'

export const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

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

export function createFakeSignature(did: string): Signature {
  return {
    id: did,
    value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd',
  }
}
