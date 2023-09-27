import { expect } from 'chai'
import { SchemaRegistry } from '../../contracts-ts'

describe('SchemaRegistry', function () {
  let schemaRegistry: SchemaRegistry

  const schemaId = 'did:2:test:1.0'
  const schema = { name: 'test' }

  beforeEach('deploy SchemaRegistry', async () => {
    schemaRegistry = await new SchemaRegistry().deploy()
  })

  describe('Add/Resolve Schema', function () {
    it('Should create and resolve Schema', async function () {
      await schemaRegistry.createSchema(schemaId, schema)
      const resolvedSchema = await schemaRegistry.resolveSchema(schemaId)

      expect(resolvedSchema).to.be.deep.equal(schema)
    })
  })
})
