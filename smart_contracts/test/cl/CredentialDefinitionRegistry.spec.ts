import { expect } from 'chai'
import { CredentialDefinitionRegistry } from '../../contracts-ts'

describe('CredentialDefinitionRegistry', function () {
  let credentialDefinitionRegistry: CredentialDefinitionRegistry

  const credentialDefinitionId = 'did:3:test:1.0'
  const credentialDefinition = { name: 'test' }

  beforeEach('deploy CredentialDefinitionRegistry', async () => {
    credentialDefinitionRegistry = await new CredentialDefinitionRegistry().deploy()
  })

  describe('Add/Resolve Credential Definition', function () {
    it('Should create and resolve Credential Definition', async function () {
      await credentialDefinitionRegistry.createCredentialDefinition(credentialDefinitionId, credentialDefinition)
      const resolvedCredentialDefinition = await credentialDefinitionRegistry.resolveCredentialDefinition(
        credentialDefinitionId,
      )

      expect(resolvedCredentialDefinition).to.be.deep.equal(credentialDefinition)
    })
  })
})
