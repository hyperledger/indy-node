import { expect } from 'chai'
import { CredentialDefinitionRegistry, DidRegistry, SchemaRegistry } from '../../contracts-ts'
import { Contract } from '../../utils'
import { TestableCredentialDefinitionRegistry, createBaseDidDocument, createCredentialDefinition, createFakeSignature, createSchema } from '../utils'
import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'

describe('CredentialDefinitionRegistry', function () {
  const issuerId = 'did:indy2:mainnet:SEp33q43PsdP7nDATyySSH'

  async function deployCredDefContractFixture() {
    const didValidator = new Contract('DidValidator')
    await didValidator.deploy()

    const didRegistry = new DidRegistry()
    await didRegistry.deploy({ libraries: [didValidator] })

    const didDocument = createBaseDidDocument(issuerId)
    const signature = createFakeSignature(issuerId)

    await didRegistry.createDid(didDocument, [signature])

    const schemaRegistry = new SchemaRegistry()
    await schemaRegistry.deploy({ params: [didRegistry.address] })

    const schema = createSchema({ issuerId: issuerId })
    await schemaRegistry.createSchema(schema)

    const credentialDefinitionRegistry  = new TestableCredentialDefinitionRegistry()
    await credentialDefinitionRegistry.deploy({ params: [didRegistry.address, schemaRegistry.address] })

    return { 
      credentialDefinitionRegistry: credentialDefinitionRegistry,
      schemaId: schema.id,
    }
  }

  describe('Add/Resolve Credential Definition', function () {
    it('Should create and resolve Credential Definition', async function () {
      const { credentialDefinitionRegistry, schemaId } = await loadFixture(deployCredDefContractFixture)

      const credDef = createCredentialDefinition({ issuerId: issuerId, schemaId: schemaId })

      await credentialDefinitionRegistry.createCredentialDefinition(credDef)
      const result = await credentialDefinitionRegistry.resolveCredentialDefinition(credDef.id)

      expect(result.credDef).to.be.deep.equal(credDef)
    })
  })
})
