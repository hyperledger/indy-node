import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import { expect } from 'chai'
import { DidRegistry } from '../../contracts-ts'
import { Contract } from '../../utils'
import { ClErrors } from '../errors'
import { createBaseDidDocument, createFakeSignature, createSchemaObject, TestableSchemaRegistry } from '../utils'

describe('SchemaRegistry', function () {
  const issuerId = 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH'

  async function deploySchemaContractFixture() {
    const didValidator = new Contract('DidValidator')
    await didValidator.deploy()

    const didRegistry = new DidRegistry()
    await didRegistry.deploy({ libraries: [didValidator] })

    const didDocument = createBaseDidDocument(issuerId)
    const signature = createFakeSignature(issuerId)

    await didRegistry.createDid(didDocument, [signature])

    const schemaRegistry = new TestableSchemaRegistry()
    await schemaRegistry.deploy({ params: [didRegistry.address] })

    return { didRegistry, schemaRegistry }
  }

  describe('Add/Resolve Schema', function () {
    it('Should create and resolve Schema', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId })

      await schemaRegistry.createSchema(schema)
      const result = await schemaRegistry.resolveSchema(schema.id)

      expect(result.schema).to.be.deep.equal(schema)
    })

    it('Should fail if resolving a non-existing schema', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId })

      await expect(schemaRegistry.resolveSchema(schema.id))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SchemaNotFound)
        .withArgs(schema.id)
    })

    it('Should fail if Schema is being created already exists', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId })

      await schemaRegistry.createSchema(schema)

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.SchemaAlreadyExist)
        .withArgs(schema.id)
    })

    it('Should fail if Schema is being created with non-existing Issuer', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId: 'did:indy2:mainnet:GEzcdDLhCpGCYRHW82kjHd' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.IssuerNotFound)
        .withArgs(schema.issuerId)
    })

    it('Should fail if Schema is being created with inactive Issuer', async function () {
      const { didRegistry, schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const signature = createFakeSignature(issuerId)
      didRegistry.deactivateDid(issuerId, [signature])

      const schema = createSchemaObject({ issuerId })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.IssuerHasBeenDeactivated)
        .withArgs(schema.issuerId)
    })

    it('Should fail if Schema is being created with empty name', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId, name: '' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('name')
    })

    it('Should fail if Schema is being created with empty version', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId, version: '' })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('version')
    })

    it('Should fail if Schema is being created without attributes', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId, attrNames: [] })

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.FieldRequired)
        .withArgs('attributes')
    })

    it('Should fail if Schema is being created with invalid Schema ID', async function () {
      const { schemaRegistry } = await loadFixture(deploySchemaContractFixture)

      const schema = createSchemaObject({ issuerId })
      schema.id = 'SEp33q43PsdP7nDATyySSH:2:BasicSchema:1.0.0'

      await expect(schemaRegistry.createSchema(schema))
        .to.be.revertedWithCustomError(schemaRegistry.baseInstance, ClErrors.InvalidSchemaId)
        .withArgs(schema.id)
    })
  })
})
