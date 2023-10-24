import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import chai from 'chai'
import { ROLES } from '../../contracts-ts'
import { Account } from '../../utils'
import { TestableRoleControl } from '../utils/contract-helpers'
import { AuthErrors } from '../utils/errors'
import { getTestAccounts, ZERO_ADDRESS } from '../utils/test-entities'

const { expect } = chai

describe('RoleControl', () => {
  async function deployRoleControlFixture() {
    const roleControl = await new TestableRoleControl().deployProxy({ params: [ZERO_ADDRESS] })
    const testAccounts = await getTestAccounts(roleControl)

    return { roleControl, testAccounts }
  }

  describe('hasRole', () => {
    it('should check role properly for an account deployer', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.deployer.account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.deployer.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.deployer.account.address)).to.equal(false)
    })

    it('should check role properly for an account without anu role assigned', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account.address)).to.equal(false)
    })

    it('should check role properly for trustee account', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.trustee.account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account.address)).to.equal(false)
    })
  })

  describe('assignRole', () => {
    it('should assign ENDORSER role by trustee', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      const account = new Account()
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)
    })

    it('should fail when assign ENDORSER role by an account without any role', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      const account = new Account()
      await expect(roleControl.connect(testAccounts.noRole.account).assignRole(ROLES.ENDORSER, account.address))
        .to.revertedWithCustomError(roleControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.noRole.account.address)
    })

    it('should override an assigned role by trustee', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      const account = new Account()

      // assign ENDORSER role
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)

      // assign STEWARD role
      await roleControl.assignRole(ROLES.STEWARD, account.address)
      expect(await roleControl.hasRole(ROLES.STEWARD, account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(false)
    })
  })

  describe('revokeRole', () => {
    it('should revoke ENDORSER role by trustee', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      const account = new Account()

      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)

      // revoke TRUSTEE role
      await roleControl.revokeRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(false)
    })

    it('should fail when revoke ENDORSER role by an account without any role', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      await expect(
        roleControl
          .connect(testAccounts.noRole.account)
          .revokeRole(ROLES.ENDORSER, testAccounts.endorser.account.address),
      )
        .to.revertedWithCustomError(roleControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.noRole.account.address)
    })
  })

  describe('getRoleCount', () => {
    it('should return assigned roles count', async function () {
      const { roleControl, testAccounts } = await loadFixture(deployRoleControlFixture)

      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.TRUSTEE, new Account().address)
      await roleControl.assignRole(ROLES.ENDORSER, new Account().address)
      await roleControl.assignRole(ROLES.ENDORSER, new Account().address)
      await roleControl.assignRole(ROLES.STEWARD, testAccounts.steward.account.address)

      expect(await roleControl.getRoleCount(ROLES.TRUSTEE)).to.equal(5)
      expect(await roleControl.getRoleCount(ROLES.ENDORSER)).to.equal(5)
      expect(await roleControl.getRoleCount(ROLES.STEWARD)).to.equal(3)
    })
  })
})
