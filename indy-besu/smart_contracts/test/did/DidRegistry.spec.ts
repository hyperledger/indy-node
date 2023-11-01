import { loadFixture } from '@nomicfoundation/hardhat-toolbox/network-helpers'
import { expect } from 'chai'
import { VerificationMethod } from '../../contracts-ts/DidRegistry'
import { RoleControl } from '../../contracts-ts/RoleControl'
import { createBaseDidDocument } from '../../utils/entity-factories'
import { deployDidRegistry } from '../utils/contract-helpers'
import { DidError } from '../utils/errors'
import { getTestAccounts, ZERO_ADDRESS } from '../utils/test-entities'

describe('DIDContract', function () {
  // We define a fixture to reuse the same setup in every test.
  // We use loadFixture to run this setup once, snapshot that state,
  // and reset Hardhat Network to that snapshot in every test.
  async function deployDidContractFixture() {
    const roleControl = await new RoleControl().deployProxy({ params: [ZERO_ADDRESS] })

    const testAccounts = await getTestAccounts(roleControl)

    const { didRegistry, didValidator, didRegex } = await deployDidRegistry()

    return { didRegistry, didValidator, didRegex, testAccounts }
  }

  describe('Create DID', function () {
    it('Should create and resolve DID document', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      console.log(JSON.stringify(didDocument))

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      const { document } = await didRegistry.resolveDid(did)

      expect(document).to.be.deep.equal(didDocument)
    })

    it('Should fail if resolving DID does not exist', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'

      await expect(didRegistry.resolveDid(did))
        .to.revertedWithCustomError(didRegistry.baseInstance, DidError.DidNotFound)
        .withArgs(did)
    })

    it('Should fail if the DID being created already exists', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      await expect(didRegistry.createDid(didDocument))
        .to.be.revertedWithCustomError(didRegistry.baseInstance, DidError.DidAlreadyExist)
        .withArgs(did)
    })

    it('Should fail if an incorrect schema is provided for the DID', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'indy:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.createDid(didDocument))
        .to.be.revertedWithCustomError(didValidator.baseInstance, DidError.IncorrectDid)
        .withArgs(did)
    })

    it('Should fail if an unsupported DID method is provided', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy3:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.createDid(didDocument))
        .to.be.revertedWithCustomError(didValidator.baseInstance, DidError.IncorrectDid)
        .withArgs(did)
    })

    it('Should fail if an incorrect DID method-specific-id is provided', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy3:testnet:123456789'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.createDid(didDocument))
        .revertedWithCustomError(didValidator.baseInstance, DidError.IncorrectDid)
        .withArgs(did)
    })

    it('Should fail if an authentication key is not provided', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)
      didDocument.authentication = []

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.createDid(didDocument))
        .revertedWithCustomError(didValidator.baseInstance, DidError.AuthenticationKeyRequired)
        .withArgs(did)
    })

    it('Should fail if an authentication key is not found in the verification methods', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

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

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.createDid(didDocument))
        .revertedWithCustomError(didValidator.baseInstance, DidError.AuthenticationKeyNotFound)
        .withArgs(didDocument.authentication[0].id)
    })
  })

  describe('Update DID', function () {
    it('Should update DID document', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      const verificationMethod: VerificationMethod = {
        id: `${did}#KEY-2`,
        verificationMethodType: 'X25519KeyAgreementKey2019',
        controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
        publicKeyMultibase: 'FbQWLPRhTH95MCkQUeFYdiSoQt8zMwetqfWoxqPgaq7x',
        publicKeyJwk: '',
      }

      didDocument.verificationMethod.push(verificationMethod)

      await didRegistry.updateDid(didDocument)

      const { document } = await didRegistry.resolveDid(did)

      expect(document).to.be.deep.equal(didDocument)
    })

    it('Should fail if the DID creator is not an update txn sender', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      didRegistry.connect(testAccounts.trustee2.account)
      await expect(didRegistry.updateDid(didDocument)).to.revertedWithCustomError(
        didRegistry.baseInstance,
        DidError.SenderIsNotCreator,
      )
    })

    it('Should fail if the DID being updated does not exists', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.updateDid(didDocument))
        .to.revertedWithCustomError(didRegistry.baseInstance, DidError.DidNotFound)
        .withArgs(did)
    })

    it('Should fail if the DID being updated is deactivated', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)
      await didRegistry.deactivateDid(did)

      await expect(didRegistry.updateDid(didDocument))
        .to.revertedWithCustomError(didRegistry.baseInstance, DidError.DidHasBeenDeactivated)
        .withArgs(did)
    })

    it('Should fail if an authentication key is not provided', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      didDocument.authentication = []

      await expect(didRegistry.updateDid(didDocument))
        .revertedWithCustomError(didValidator.baseInstance, DidError.AuthenticationKeyRequired)
        .withArgs(did)
    })

    it('Should fail if an authentication key is not found in the verification methods', async function () {
      const { didRegistry, didValidator, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

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

      await expect(didRegistry.updateDid(didDocument))
        .revertedWithCustomError(didValidator.baseInstance, DidError.AuthenticationKeyNotFound)
        .withArgs(didDocument.authentication[0].id)
    })
  })

  describe('Deactivate DID', function () {
    it('Should deactivate DID document', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)
      await didRegistry.deactivateDid(did)

      const didStorage = await didRegistry.resolveDid(did)

      expect(didStorage.metadata.deactivated).is.true
    })

    it('Should fail if the DID has already been deactivated', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)
      await didRegistry.deactivateDid(did)

      await expect(didRegistry.deactivateDid(did))
        .to.revertedWithCustomError(didRegistry.baseInstance, DidError.DidHasBeenDeactivated)
        .withArgs(did)
    })

    it('Should fail if the DID being deactivated does not exists', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'

      didRegistry.connect(testAccounts.trustee.account)
      await expect(didRegistry.deactivateDid(did))
        .to.revertedWithCustomError(didRegistry.baseInstance, DidError.DidNotFound)
        .withArgs(did)
    })

    it('Should fail if the DID creator is not an deactivate txn sender', async function () {
      const { didRegistry, testAccounts } = await loadFixture(deployDidContractFixture)

      const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
      const didDocument = createBaseDidDocument(did)

      didRegistry.connect(testAccounts.trustee.account)
      await didRegistry.createDid(didDocument)

      didRegistry.connect(testAccounts.trustee2.account)
      await expect(didRegistry.deactivateDid(didDocument.id)).to.revertedWithCustomError(
        didRegistry.baseInstance,
        DidError.SenderIsNotCreator,
      )
    })
  })
})
