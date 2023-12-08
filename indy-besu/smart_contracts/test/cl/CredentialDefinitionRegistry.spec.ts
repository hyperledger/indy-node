import { expect } from 'chai'
import { IndyDidRegistry } from '../../contracts-ts'
import { createCredentialDefinitionObject } from '../../utils'
import {
  createDid,
  createSchema,
  deployCredentialDefinitionRegistry,
  TestableCredentialDefinitionRegistry,
  TestableSchemaRegistry,
} from '../utils/contract-helpers'
import { ClErrors } from '../utils/errors'
import { TestAccounts } from '../utils/test-entities'

describe('CredentialDefinitionRegistry', function () {
  let didRegistry: IndyDidRegistry
  let schemaRegistry: TestableSchemaRegistry
  let credentialDefinitionRegistry: TestableCredentialDefinitionRegistry
  let testAccounts: TestAccounts
  let schemaId: string
  const issuerId = 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH'

  beforeEach(async function () {
    const {
      indyDidRegistry: didRegistryInit,
      schemaRegistry: schemaRegistryInit,
      credentialDefinitionRegistry: credentialDefinitionRegistryInit,
      testAccounts: testAccountsInit,
    } = await deployCredentialDefinitionRegistry()

    didRegistryInit.connect(testAccountsInit.trustee.account)
    schemaRegistryInit.connect(testAccountsInit.trustee.account)
    credentialDefinitionRegistryInit.connect(testAccountsInit.trustee.account)
    await createDid(didRegistryInit, issuerId)
    const schema = await createSchema(schemaRegistryInit, issuerId)

    didRegistry = didRegistryInit
    testAccounts = testAccountsInit
    schemaRegistry = schemaRegistryInit
    credentialDefinitionRegistry = credentialDefinitionRegistryInit
    schemaId = schema.id
  })

  describe('Add/Resolve Credential Definition', function () {
    it('Should create and resolve Credential Definition', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId })

      await credentialDefinitionRegistry.createCredentialDefinition(credDef)
      const result = await credentialDefinitionRegistry.resolveCredentialDefinition(credDef.id)

      expect(result.credDef).to.be.deep.equal(credDef)
    })

    it('Should fail if resolving Credential Definition does not exist', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId })

      await expect(credentialDefinitionRegistry.resolveCredentialDefinition(credDef.id))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.CredentialDefinitionNotFound)
        .withArgs(credDef.id)
    })

    it('Should fail if Credential Definition is being already exists', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId })

      await credentialDefinitionRegistry.createCredentialDefinition(credDef)

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(
          credentialDefinitionRegistry.baseInstance,
          ClErrors.CredentialDefinitionAlreadyExist,
        )
        .withArgs(credDef.id)
    })

    it('Should fail if Credential Definition is being created with non-existing Issuer', async function () {
      const credDef = createCredentialDefinitionObject({
        issuerId: 'did:indy2:mainnet:GEzcdDLhCpGCYRHW82kjHd',
        schemaId,
      })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.IssuerNotFound)
        .withArgs(credDef.issuerId)
    })

    it('Should fail if Credential Definition is being created with inactive Issuer', async function () {
      didRegistry.deactivateDid(issuerId)

      const credDef = createCredentialDefinitionObject({ issuerId, schemaId })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.IssuerHasBeenDeactivated)
        .withArgs(credDef.issuerId)
    })

    it('Should fail if Credential Definition is being created with non-existing Schema', async function () {
      const credDef = createCredentialDefinitionObject({
        issuerId,
        schemaId: 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH/anoncreds/v0/SCHEMA/Test/1.0.0',
      })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SchemaNotFound)
        .withArgs(credDef.schemaId)
    })

    it('Should fail if Credential Definition is being created with unsupported type', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId, credDefType: 'CL2' })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(
          credentialDefinitionRegistry.baseInstance,
          ClErrors.UnsupportedCredentialDefinitionType,
        )
        .withArgs(credDef.credDefType)
    })

    it('Should fail if Credential Definition is being created with empty tag', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId, tag: '' })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('tag')
    })

    it('Should fail if Credential Definition is being created with empty value', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId, value: '' })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('value')
    })

    it('Should fail if Credential Definition is being created with not owned Issuer DID', async function () {
      const issuerId2 = 'did:indy2:mainnet:SEp33q43PsdP7nDATyyDDA'
      const credDef = createCredentialDefinitionObject({ issuerId, schemaId })

      didRegistry.connect(testAccounts.trustee2.account)
      credentialDefinitionRegistry.connect(testAccounts.trustee2.account)

      await createDid(didRegistry, issuerId2)
      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.SenderIsNotIssuerDidOwner)
        .withArgs(testAccounts.trustee2.account.address, testAccounts.trustee.account.address)
    })

    // FIXME: for ledger migration purpose we disabled checking id validity for credential definition
    //  as it can contain schema id represented as seq_no
    // it('Should fail if Credential Definition is being with invalid ID', async function () {
    //   const { credentialDefinitionRegistry, schemaId } = await loadFixture(deployCredDefContractFixture)
    //
    //   const credDef = createCredentialDefinitionObject({ issuerId, schemaId })
    //   credDef.id = 'Gs6cQcvrtWoZKsbBhD3dQJ:3:CL:140384:mctc'
    //
    //   await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
    //     .to.be.revertedWithCustomError(
    //       credentialDefinitionRegistry.baseInstance,
    //       ClErrors.InvalidCredentialDefinitionId,
    //     )
    //     .withArgs(credDef.id)
    // })
  })

  describe('Add/Resolve Credential Definition with did:ethr Issuer', function () {
    it('Should create and resolve Credential Definition', async function () {
      const ethrIssuerId = `did:ethr:${testAccounts.trustee.account.address}`
      const credDef = createCredentialDefinitionObject({ issuerId: ethrIssuerId, schemaId })

      await credentialDefinitionRegistry.createCredentialDefinition(credDef)
      const result = await credentialDefinitionRegistry.resolveCredentialDefinition(credDef.id)

      expect(result.credDef).to.be.deep.equal(credDef)
    })

    it('Should fail if Credential Definition is being created with not owned Issuer DID', async function () {
      const ethrIssuerId = `did:ethr:${testAccounts.trustee2.account.address}`
      const credDef = createCredentialDefinitionObject({ issuerId: ethrIssuerId, schemaId })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(credentialDefinitionRegistry.baseInstance, ClErrors.SenderIsNotIssuerDidOwner)
        .withArgs(testAccounts.trustee.account.address, testAccounts.trustee2.account.address)
    })

    it('Should fail if Credential Definition is being created with invalid Issuer ID', async function () {
      const credDef = createCredentialDefinitionObject({ issuerId: 'did:ethr:ab$ddfgh354345', schemaId })

      await expect(credentialDefinitionRegistry.createCredentialDefinition(credDef))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.InvalidIssuerId)
        .withArgs(credDef.issuerId)
    })
  })
})
