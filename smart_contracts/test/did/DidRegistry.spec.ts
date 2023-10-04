import { loadFixture } from '@nomicfoundation/hardhat-toolbox/network-helpers'
import { expect } from 'chai'
import { DidRegistry, VerificationMethod } from '../../contracts-ts/DidRegistry'
import { Contract } from '../../utils'
import { createBaseDidDocument, createFakeSignature, deployDidRegistry } from '../utils'

describe('DIDContract', function () {
  // We define a fixture to reuse the same setup in every test.
  // We use loadFixture to run this setup once, snapshot that state,
  // and reset Hardhat Network to that snapshot in every test.
  async function deployDidContractFixture() {
    return deployDidRegistry()
  }

  describe('Create DID', function () {
    it('Should create and resolve DID document', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      const { document } = await didRegistry.resolveDid(did)

      expect(document).to.be.deep.equal(didDocument)
    })

    it('Should fail if resolving DID does not exist', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'

      await expect(didRegistry.resolveDid(did)).to.be.revertedWith('DID not found')
    })

    it('Should create DID document when UUID is provided as DID method-specific-id', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:03043e53-4d36-44f2-9996-a839634f48f9'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      const { document } = await didRegistry.resolveDid(did)

      expect(document).to.be.deep.equal(didDocument)
    })

    it('Should fail if the DID being created already exists', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('DID has already exist')
    })

    it('Should fail if an incorrect schema is provided for the DID', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'indy:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Incorrect DID')
    })

    it('Should fail if an unsupported DID method is provided', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy3:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Incorrect DID')
    })

    it('Should fail if an incorrect DID method-specific-id is provided', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy3:testnet:123456789'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Incorrect DID')
    })

    it('Should fail if an authentication key is not provided', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      didDocument.authentication = []
      const signature = createFakeSignature(did)

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Authentication key is required')
    })

    it('Should fail if an authentication key is not found in the verification methods', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      didDocument.authentication = [
        {
          id: `${did}#KEY-3`,
          verificationMethod: {
            id: '',
            verificationMethodType: '',
            controller: '',
            publicKeyMultibase: '',
            publicKeyJwk: '',
          },
        },
      ]
      const signature = createFakeSignature(did)

      await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith(
        `Authentication key for ID: ${did}#KEY-3 is not found`,
      )
    })
  })

  describe('Update DID', function () {
    it('Should update DID document', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      const verificationMethod: VerificationMethod = {
        id: `${did}#KEY-2`,
        verificationMethodType: 'X25519KeyAgreementKey2019',
        controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
        publicKeyMultibase: 'FbQWLPRhTH95MCkQUeFYdiSoQt8zMwetqfWoxqPgaq7x',
        publicKeyJwk: '',
      }

      didDocument.verificationMethod.push(verificationMethod)

      await didRegistry.updateDid(didDocument, [signature])

      const { document } = await didRegistry.resolveDid(did)

      expect(document).to.be.deep.equal(didDocument)
    })

    it('Should fail if the DID being updated does not exists', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith('DID not found')
    })

    it('Should fail if the DID being updated is deactivated', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])
      await didRegistry.deactivateDid(did, [signature])

      await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith('DID has been deactivated')
    })

    it('Should fail if an authentication key is not provided', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      didDocument.authentication = []

      await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith('Authentication key is required')
    })

    it('Should fail if an authentication key is not found in the verification methods', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])

      didDocument.authentication = [
        {
          id: `${did}#KEY-3`,
          verificationMethod: {
            id: '',
            verificationMethodType: '',
            controller: '',
            publicKeyMultibase: '',
            publicKeyJwk: '',
          },
        },
      ]

      await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith(
        `Authentication key for ID: ${did}#KEY-3 is not found`,
      )
    })
  })

  describe('Deactivate DID', function () {
    it('Should deactivate DID document', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])
      await didRegistry.deactivateDid(did, [signature])

      const didStorage = await didRegistry.resolveDid(did)

      expect(didStorage.metadata.deactivated).is.true
    })

    it('Should fail if the DID has already been deactivated', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      const signature = createFakeSignature(did)

      await didRegistry.createDid(didDocument, [signature])
      await didRegistry.deactivateDid(did, [signature])

      await expect(didRegistry.deactivateDid(did, [signature])).to.be.revertedWith('DID has been deactivated')
    })

    it('Should fail if the DID being deactivated does not exists', async function () {
      const didRegistry = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const signature = createFakeSignature(did)

      await expect(didRegistry.deactivateDid(did, [signature])).to.be.revertedWith('DID not found')
    })
  })
})
