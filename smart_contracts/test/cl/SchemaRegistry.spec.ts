import { expect } from 'chai'
import { SchemaRegistry } from '../../contracts-ts/SchemaRegistry'
import { RoleControl } from '../../contracts-ts/RoleControl'
import { getTestAccounts, TestAccounts } from '../utils'

describe('SchemaRegistry', function () {
  let roleControl: RoleControl
  let schemaRegistry: SchemaRegistry
  let testAccounts: TestAccounts

  const schemaId = 'did:2:test:1.0'
  const schema = { name: 'test' }

  beforeEach('deploy ValidatorSmartContract', async () => {
    roleControl = await new RoleControl().deploy()
    testAccounts = await getTestAccounts(roleControl)
    schemaRegistry = await new SchemaRegistry().deploy([roleControl.address])
  })

  describe('Add/Resolve Schema', function () {
    it('Should create DID document', async function () {
      await schemaRegistry.connect(testAccounts.trustee.account).create(schemaId, schema)
      const resolvedSchema = await schemaRegistry.resolve(schemaId)

      expect(resolvedSchema).to.be.deep.equal(schema)
    })
  })
})
