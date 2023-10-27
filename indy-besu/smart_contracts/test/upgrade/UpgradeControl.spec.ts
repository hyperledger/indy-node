import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import chai from 'chai'
import { RoleControl } from '../../contracts-ts'
import { TestableUpgradeControl, UpgradablePrototype } from '../utils/contract-helpers'
import { AuthErrors, ProxyError, UpgradeControlErrors } from '../utils/errors'
import { ProxyEvents, UpgradeControlEvents } from '../utils/events'
import { getTestAccounts, ZERO_ADDRESS } from '../utils/test-entities'

const { expect } = chai

describe('UpgradableControl', function () {
  async function deployUpgradableContractFixture() {
    const roleControl = await new RoleControl().deployProxy({ params: [ZERO_ADDRESS] })

    const testAccounts = await getTestAccounts(roleControl)

    const upgradeControl = await new TestableUpgradeControl().deployProxy({ params: [roleControl.address] })

    const upgradablePrototype = await new UpgradablePrototype('UpgradablePrototypeV1').deployProxy({
      params: [upgradeControl.address],
    })

    const upgradablePrototypeV2 = await new UpgradablePrototype('UpgradablePrototypeV2').deploy()

    return { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts }
  }

  describe('Propose and approve contract', function () {
    it('Should upgrade the proposed contract once sufficient approvals are received', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose and approve by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)

      // Approve by trustee2
      upgradeControl.connect(testAccounts.trustee2.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee2.account.address)

      // Approve by trustee3
      upgradeControl.connect(testAccounts.trustee3.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradablePrototype.baseInstance, ProxyEvents.Upgraded)
        .withArgs(upgradablePrototypeV2.address)
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee3.account.address)

      expect(upgradeControl.ensureSufficientApprovals(upgradablePrototype.address!, upgradablePrototypeV2.address!)).to
        .not.reverted
      expect(await upgradablePrototype.version).to.be.equal(await upgradablePrototypeV2.version)
    })

    it('Should not upgrade the proposed contract without receiving sufficient approvals', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose and approve by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)

      // Approve by trustee2
      upgradeControl.connect(testAccounts.trustee2.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee2.account.address)

      expect(
        upgradeControl.ensureSufficientApprovals(upgradablePrototype.address!, upgradablePrototypeV2.address!),
      ).revertedWithCustomError(upgradeControl.baseInstance, UpgradeControlErrors.InsufficientApprovals)
      expect(await upgradablePrototype.version).to.be.not.equal(await upgradablePrototypeV2.version)
    })
  })

  describe('Propose negative cases', function () {
    it('Should fail when propose sends from a non-trustee account', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose by endorser
      upgradeControl.connect(testAccounts.endorser.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.endorser.account.address)

      // Propose by steward
      upgradeControl.connect(testAccounts.steward.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.steward.account.address)

      // Propose by account without role
      upgradeControl.connect(testAccounts.noRole.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.noRole.account.address)
    })

    it('Should fail when an implementation that is not UUPSUpgradable is proposed', async function () {
      const { upgradeControl, upgradablePrototype, testAccounts } = await loadFixture(deployUpgradableContractFixture)

      const notUpgradable = await new UpgradablePrototype('NotUpgradable').deploy()

      // Propose by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, notUpgradable.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, ProxyError.ERC1967InvalidImplementation)
        .withArgs(notUpgradable.address)
    })

    it('Should fail when the same implementation upgrade is proposed twice', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose upgrade by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)

      // Propose same upgrade by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, UpgradeControlErrors.UpgradeAlreadyProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address)
    })
  })

  describe('Approve negative cases', function () {
    it('Should fail when the trustee has already approved the implementation upgrade', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose and approve by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeApproved)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)

      await expect(
        upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!),
      ).to.revertedWithCustomError(upgradeControl.baseInstance, UpgradeControlErrors.UpgradeAlreadyApproved)
    })

    it('Should fail when approval sends from a non-trustee account', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.propose(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.emit(upgradeControl.baseInstance, UpgradeControlEvents.UpgradeProposed)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address, testAccounts.trustee.account.address)

      // Approve by endorser
      upgradeControl.connect(testAccounts.endorser.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.endorser.account.address)

      // Approve by steward
      upgradeControl.connect(testAccounts.steward.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.steward.account.address)

      // Approve by account without role
      upgradeControl.connect(testAccounts.noRole.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.noRole.account.address)
    })

    it('Should fail when approval sends to an unproposed upgrade', async function () {
      const { upgradeControl, upgradablePrototype, upgradablePrototypeV2, testAccounts } = await loadFixture(
        deployUpgradableContractFixture,
      )

      // Propose by trustee
      upgradeControl.connect(testAccounts.trustee.account)
      await expect(upgradeControl.approve(upgradablePrototype.address!, upgradablePrototypeV2.address!))
        .to.revertedWithCustomError(upgradeControl.baseInstance, UpgradeControlErrors.UpgradeProposalNotFound)
        .withArgs(upgradablePrototype.address, upgradablePrototypeV2.address)
    })
  })
})
