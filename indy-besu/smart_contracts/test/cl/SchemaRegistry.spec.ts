import { expect } from 'chai'
import { IndyDidRegistry, SchemaRegistry } from '../../contracts-ts'
import { createSchemaObject } from '../../utils'
import { createDid, deploySchemaRegistry, TestableSchemaRegistry } from '../utils/contract-helpers'
import { ClErrors } from '../utils/errors'
import { TestAccounts } from '../utils/test-entities'

describe('SchemaRegistry', function () {
  let didRegistry: IndyDidRegistry
  let schemaRegistry: TestableSchemaRegistry
  let testAccounts: TestAccounts
  const issuerId = 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH'

  beforeEach(async function () {
    const {
      indyDidRegistry: didRegistryInit,
      schemaRegistry: schemaRegistryInit,
      testAccounts: testAccountsInit,
    } = await deploySchemaRegistry()

    didRegistryInit.connect(testAccountsInit.trustee.account)
    schemaRegistryInit.connect(testAccountsInit.trustee.account)
    await createDid(didRegistryInit, issuerId)

    didRegistry = didRegistryInit
    testAccounts = testAccountsInit
    schemaRegistry = schemaRegistryInit
  })

  describe('Add/Resolve Schema', function () {
    it('Should create and resolve Schema', async function () {
      const schema = createSchemaObject({ issuerId })

      await schemaRegistry.createSchema(schema)
      const result = await schemaRegistry.resolveSchema(schema.id)

      expect(result.schema).to.be.deep.equal(schema)
    })

    it('Should fail if resolving a non-existing schema', async function () {
      const schema = createSchemaObject({ issuerId })

      await expect(schemaRegistry.resolveSchema(schema.id))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SchemaNotFound)
        .withArgs(schema.id)
    })

    it('Should fail if Schema is being created already exists', async function () {
      const schema = createSchemaObject({ issuerId })

      await schemaRegistry.createSchema(schema)

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SchemaAlreadyExist)
        .withArgs(schema.id)
    })

    it('Should fail if Schema is being created with non-existing Issuer', async function () {
      const schema = createSchemaObject({ issuerId: 'did:indy2:mainnet:GEzcdDLhCpGCYRHW82kjHd' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.IssuerNotFound)
        .withArgs(schema.issuerId)
    })

    it('Should fail if Schema is being created with inactive Issuer', async function () {
      didRegistry.deactivateDid(issuerId)

      const schema = createSchemaObject({ issuerId })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.IssuerHasBeenDeactivated)
        .withArgs(schema.issuerId)
    })

    it('Should fail if Schema is being created with empty name', async function () {
      const schema = createSchemaObject({ issuerId, name: '' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('name')
    })

    it('Should fail if Schema is being created with empty version', async function () {
      const schema = createSchemaObject({ issuerId, version: '' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('version')
    })

    it('Should fail if Schema is being created without attributes', async function () {
      const schema = createSchemaObject({ issuerId, attrNames: [] })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('attributes')
    })

    it('Should fail if Schema is being created with invalid Schema ID', async function () {
      const schema = createSchemaObject({ issuerId })
      schema.id = 'SEp33q43PsdP7nDATyySSH:2:BasicSchema:1.0.0'

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.InvalidSchemaId)
        .withArgs(schema.id)
    })

    it('Should fail if Schema is being created with not owned Issuer DID', async function () {
      const issuerId2 = 'did:indy2:mainnet:SEp33q43PsdP7nDATyyDDA'
      const schema = createSchemaObject({ issuerId })

      didRegistry.connect(testAccounts.trustee2.account)
      schemaRegistry.connect(testAccounts.trustee2.account)

      await createDid(didRegistry, issuerId2)
      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SenderIsNotIssuerDidOwner)
        .withArgs(testAccounts.trustee2.account.address, testAccounts.trustee.account.address)
    })
  })

  describe('Add/Resolve Schema with did:ethr Issuer', function () {
    it('Should create and resolve Schema', async function () {
      const ethrIssuerId = `did:ethr:${testAccounts.trustee.account.address}`

      const schema = createSchemaObject({ issuerId: ethrIssuerId })

      await schemaRegistry.createSchema(schema)
      const result = await schemaRegistry.resolveSchema(schema.id)

      expect(result.schema).to.be.deep.equal(schema)
    })

    it('Should fail if Schema is being created with not owned Issuer DID', async function () {
      const ethrIssuerId = `did:ethr:${testAccounts.trustee2.account.address}`

      const schema = createSchemaObject({ issuerId: ethrIssuerId })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SenderIsNotIssuerDidOwner)
        .withArgs(testAccounts.trustee.account.address, testAccounts.trustee2.account.address)
    })

    it('Should fail if Schema is being created with invalid Issuer ID', async function () {
      const schema = createSchemaObject({ issuerId: 'did:ethr:ab$ddfgh354345' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.InvalidIssuerId)
        .withArgs(schema.issuerId)
    })
  })
})
