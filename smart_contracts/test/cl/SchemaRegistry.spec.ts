import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import { expect } from 'chai'
import { DidRegistry, SchemaRegistry } from '../../contracts-ts'
import { Contract } from '../../utils'
import { createBaseDidDocument, createFakeSignature, createSchemaData } from '../utils'

describe('SchemaRegistry', function () {
  const issuerId = 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH'

  async function deploySchemaContractFixture() {
    const didValidator = new Contract('DidValidator')
    await didValidator.deploy()

    const didRegistry = new DidRegistry()
    await didRegistry.deploy({ libraries: [didValidator] })

    const schemaValidator = new Contract('SchemaValidator')
    await schemaValidator.deploy()

    const didDocument = createBaseDidDocument(issuerId)
    const signature = createFakeSignature(issuerId)

    await didRegistry.createDid(didDocument, [signature])

    return new SchemaRegistry().deploy({ params: [didRegistry.address], libraries: [schemaValidator] })
  }

  describe('Add/Resolve Schema', function () {
    it('Should create and resolve Schema', async function () {
      const schemaRegistry = await loadFixture(deploySchemaContractFixture)

      const schemaData = createSchemaData(issuerId)

      await schemaRegistry.createSchema(schemaData)
      const resolvedSchema = await schemaRegistry.resolveSchema(schemaData.id)

      expect(resolvedSchema.data).to.be.deep.equal(schemaData)
    })
  })

  it('Should fail if the Schema ID already exists', async function () {})
})
