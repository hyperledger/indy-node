import chai from 'chai'
import { getTestAccounts, TestAccounts } from '../utils'
import { RoleControl, ROLES } from '../../contracts-ts/RoleControl'
import { Account } from '../../utils/account'

const { expect } = chai

describe('RoleControl', () => {
  let roleControl: RoleControl
  let testAccounts: TestAccounts

  beforeEach('deploy RoleControl', async () => {
    roleControl = await new RoleControl().deploy()
    testAccounts = await getTestAccounts(roleControl)
  })

  describe('hasRole', () => {
    it('should check role properly for an account deployer', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.deployer.account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.deployer.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.deployer.account.address)).to.equal(false)
    })

    it('should check role properly for an account without anu role assigned', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account.address)).to.equal(false)
    })

    it('should check role properly for trustee account', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.trustee.account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account.address)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account.address)).to.equal(false)
    })
  })

  describe('assignRole', () => {
    it('should assign ENDORSER role by trustee', async function () {
      const account = new Account()
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)
    })

    it('should fail when assign ENDORSER role by an account without any role', async function () {
      const account = new Account()
      await expect(
        roleControl.connect(testAccounts.noRole.account).assignRole(ROLES.ENDORSER, account.address),
      ).to.be.revertedWith('Sender does not have required role to perform action')
    })

    it('should override an assigned role by trustee', async function () {
      const account = new Account()

      // assign ENDORSER role
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)

      // assign STEWARD role
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.STEWARD, account.address)
      expect(await roleControl.hasRole(ROLES.STEWARD, account.address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(false)
    })
  })

  describe('revokeRole', () => {
    it('should revoke ENDORSER role by trustee', async function () {
      const account = new Account()

      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(true)

      // revoke TRUSTEE role
      await roleControl.connect(testAccounts.trustee.account).revokeRole(ROLES.ENDORSER, account.address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account.address)).to.equal(false)
    })

    it('should fail when revoke ENDORSER role by an account without any role', async function () {
      await expect(
        roleControl
          .connect(testAccounts.noRole.account)
          .revokeRole(ROLES.ENDORSER, testAccounts.endorser.account.address),
      ).to.be.revertedWith('Sender does not have required role to perform action')
    })
  })
})
