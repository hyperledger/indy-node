import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import { expect } from 'chai'
import { createBaseDidDocument } from '../../utils'
import { deployUniversalDidResolver, TestableUniversalDidResolver } from '../utils/contract-helpers'
import { DidError } from '../utils/errors'
import { TestAccounts } from '../utils/test-entities'

describe('UniversalDidResolver', function () {
  const indy2DidDocument = createBaseDidDocument('did:indy2:testnet:SEp33q43PsdP7nDATyySSH')
  let universalDidReolver: TestableUniversalDidResolver
  let testAccounts: TestAccounts

  async function deployUniversalDidResolverFixture() {
    const {
      universalDidReolver: universalDidReolverInit,
      indyDidRegistry,
      testAccounts: testAccountsInit,
    } = await deployUniversalDidResolver()

    indyDidRegistry.connect(testAccountsInit.trustee.account)
    await indyDidRegistry.createDid(indy2DidDocument)

    return { universalDidReolverInit, testAccountsInit }
  }

  beforeEach(async function () {
    const { universalDidReolverInit, testAccountsInit } = await loadFixture(deployUniversalDidResolverFixture)

    universalDidReolver = universalDidReolverInit
    testAccounts = testAccountsInit

    universalDidReolver.connect(testAccounts.trustee.account)
  })

  describe('Resolve did:indy2', function () {
    it('Should resolve DID document', async function () {
      const document = await universalDidReolver.resolveDocument(indy2DidDocument.id)

      expect(document).to.be.deep.equal(indy2DidDocument)
    })

    it('Should resolve DID metadata', async function () {
      const metadata = await universalDidReolver.resolveMetadata(indy2DidDocument.id)

      expect(metadata).to.contain({
        creator: testAccounts.trustee.account.address,
        deactivated: false,
      })
    })
  })

  describe('Resolve did:ethr', function () {
    it('Should resolve DID metadata', async function () {
      const metadata = await universalDidReolver.resolveMetadata(`did:ethr:${testAccounts.trustee.account.address}`)

      expect(metadata).to.contain({
        creator: testAccounts.trustee.account.address,
        deactivated: false,
      })
    })

    it('Should fail if an incorrect DID method-specific-id is provided', async function () {
      const incorrectDid = 'did:ethr:ab$ddfgh354345'

      await expect(universalDidReolver.resolveMetadata(incorrectDid))
        .revertedWithCustomError(universalDidReolver.baseInstance, DidError.IncorrectDid)
        .withArgs(incorrectDid)
    })
  })
})
