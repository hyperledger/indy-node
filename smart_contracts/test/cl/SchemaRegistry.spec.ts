import { expect } from 'chai'
import { SchemaRegistry } from '../../contracts-ts'

describe('SchemaRegistry', function () {
  let schemaRegistry: SchemaRegistry

  const schemaId = 'did:2:test:1.0'
  const schema = { name: 'test' }

  beforeEach('deploy ValidatorSmartContract', async () => {
    schemaRegistry = await new SchemaRegistry().deploy()
  })

  describe('Add/Resolve Schema', function () {
    it('Should create DID document', async function () {
      await schemaRegistry.create(schemaId, schema)
      const resolvedSchema = await schemaRegistry.resolve(schemaId)

      expect(resolvedSchema).to.be.deep.equal(schema)
    })
  })
})
