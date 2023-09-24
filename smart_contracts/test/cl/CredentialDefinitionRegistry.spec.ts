import { expect } from 'chai'
import { CredentialDefinitionRegistry } from '../../contracts-ts'

describe('CredentialDefinitionRegistry', function () {
  let credentialDefinitionRegistry: CredentialDefinitionRegistry

  const credentialDefinitionId = 'did:3:test:1.0'
  const credentialDefinition = { name: 'test' }

  beforeEach('deploy ValidatorSmartContract', async () => {
    credentialDefinitionRegistry = await new CredentialDefinitionRegistry().deploy()
  })

  describe('Add/Resolve Credential Definition', function () {
    it('Should create DID document', async function () {
      await credentialDefinitionRegistry.createCredentialDefinition(credentialDefinitionId, credentialDefinition)
      const resolvedCredentialDefinition = await credentialDefinitionRegistry.resolveCredentialDefinition(credentialDefinitionId)

      expect(resolvedCredentialDefinition).to.be.deep.equal(credentialDefinition)
    })
  })
})
