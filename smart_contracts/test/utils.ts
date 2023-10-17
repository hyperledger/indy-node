import { HardhatEthersSigner } from '@nomicfoundation/hardhat-ethers/signers'
import { BytesLike } from 'ethers'
import { ethers } from 'hardhat'
import {
  CredentialDefinition,
  CredentialDefinitionRegistry,
  DidDocument,
  DidRegistry,
  ROLES,
  Schema,
  SchemaRegistry,
  Transaction,
  UpgradeControl,
  VerificationMethod,
  VerificationRelationship,
} from '../contracts-ts'
import { Contract } from '../utils'

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

export class TestableDidRegistry extends DidRegistry {
  public get baseInstance() {
    return this.instance
  }
}

export class TestableSchemaRegistry extends SchemaRegistry {
  public get baseInstance() {
    return this.instance
  }
}

export class TestableCredentialDefinitionRegistry extends CredentialDefinitionRegistry {
  public get baseInstance() {
    return this.instance
  }
}

export class TestableUpgradeControl extends UpgradeControl {
  public get baseInstance() {
    return this.instance
  }
}

export class UpgradablePrototype extends Contract {
  public get baseInstance() {
    return this.instance
  }

  public get version(): Promise<string> {
    return this.instance.getVersion()
  }
}

export async function deployDidRegistry() {
  const didRegex = new Contract('DidRegex')
  await didRegex.deploy()

  const didValidator = new Contract('DidValidator')
  await didValidator.deploy({ libraries: [didRegex] })

  const didRegistry = new TestableDidRegistry()
  await didRegistry.deploy({ libraries: [didValidator] })

  return didRegistry
}

export async function deploySchemaRegistry() {
  const didRegistry = await deployDidRegistry()

  const schemaRegistry = new TestableSchemaRegistry()
  await schemaRegistry.deploy({ params: [didRegistry.address] })

  return { didRegistry, schemaRegistry }
}

export async function deployCredentialDefinitionRegistry() {
  const { didRegistry, schemaRegistry } = await deploySchemaRegistry()

  const credentialDefinitionRegistry = new TestableCredentialDefinitionRegistry()
  await credentialDefinitionRegistry.deploy({ params: [didRegistry.address, schemaRegistry.address] })

  return { credentialDefinitionRegistry, didRegistry, schemaRegistry }
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

export function createContractDeployTransaction(sender: string): Transaction {
  return {
    sender,
    target: '0x0000000000000000000000000000000000000000',
    value: 0,
    gasPrice: 0,
    gasLimit: 0,
    bytes: '0x00',
  }
}

export function createWriteTransaction(sender: string): Transaction {
  return {
    sender,
    target: '0x0000000000000000000000000000000000003333',
    value: 0,
    gasPrice: 0,
    gasLimit: 0,
    bytes: '0x00',
  }
}
