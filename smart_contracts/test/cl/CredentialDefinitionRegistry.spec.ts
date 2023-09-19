import { expect } from 'chai'
import { RoleControl } from '../../contracts-ts/RoleControl'
import { getTestAccounts, TestAccounts } from '../utils'
import { CredentialDefinitionRegistry } from '../../contracts-ts/CredentialDefinitionRegistry'

describe('CredentialDefinitionRegistry', function () {
  let roleControl: RoleControl
  let credentialDefinitionRegistry: CredentialDefinitionRegistry
  let testAccounts: TestAccounts

  const credentialDefinitionId = 'did:3:test:1.0'
  const credentialDefinition = { name: 'test' }

  beforeEach('deploy ValidatorSmartContract', async () => {
    roleControl = await new RoleControl().deploy()
    testAccounts = await getTestAccounts(roleControl)
    credentialDefinitionRegistry = await new CredentialDefinitionRegistry().deploy([roleControl.address])
  })

  describe('Add/Resolve Credential Definition', function () {
    it('Should create DID document', async function () {
      await credentialDefinitionRegistry
        .connect(testAccounts.trustee.account)
        .create(credentialDefinitionId, credentialDefinition)
      const resolvedCredentialDefinition = await credentialDefinitionRegistry.resolve(credentialDefinitionId)

      expect(resolvedCredentialDefinition).to.be.deep.equal(credentialDefinition)
    })
  })
})
