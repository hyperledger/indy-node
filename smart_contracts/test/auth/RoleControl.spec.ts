import { ethers } from 'hardhat'

import chai from 'chai'
import { getTestAccounts, ROLES, TestAccounts, web3 } from '../utils'

const { expect } = chai

describe('RoleControl', () => {
  let roleControl: any
  let testAccounts: TestAccounts

  before('deploy RoleControl', async () => {
    roleControl = await ethers.deployContract('RoleControl')
    testAccounts = await getTestAccounts(roleControl)
  })

  describe('hasRole', () => {
    it('should check role properly for an account deployer', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.deployer.account)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.deployer.account)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.deployer.account)).to.equal(false)
    })

    it('should check role properly for an account without anu role assigned', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.noRole.account)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account)).to.equal(false)
    })

    it('should check role properly for trustee account', async function () {
      expect(await roleControl.hasRole(ROLES.TRUSTEE, testAccounts.trustee.account)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, testAccounts.noRole.account)).to.equal(false)
      expect(await roleControl.hasRole(ROLES.STEWARD, testAccounts.noRole.account)).to.equal(false)
    })
  })

  describe('assignRole', () => {
    it('should assign ENDORSER role by trustee', async function () {
      const account = web3.eth.accounts.create().address
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, account)
      expect(await roleControl.hasRole(ROLES.ENDORSER, account)).to.equal(true)
    })

    it('should fail when assign ENDORSER role by an account without any role', async function () {
      const account = web3.eth.accounts.create().address
      await expect(
        roleControl.connect(testAccounts.noRole.account).assignRole(ROLES.ENDORSER, account),
      ).to.be.rejectedWith(
        Error,
        "VM Exception while processing transaction: reverted with reason string 'Sender does not have required role to perform action",
      )
    })

    it('should override an assigned role by trustee', async function () {
      const address = web3.eth.accounts.create().address

      // assign ENDORSER role
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, address)).to.equal(true)

      // assign STEWARD role
      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.STEWARD, address)
      expect(await roleControl.hasRole(ROLES.STEWARD, address)).to.equal(true)
      expect(await roleControl.hasRole(ROLES.ENDORSER, address)).to.equal(false)
    })
  })

  describe('revokeRole', () => {
    it('should revoke ENDORSER role by trustee', async function () {
      const address = web3.eth.accounts.create().address

      await roleControl.connect(testAccounts.trustee.account).assignRole(ROLES.ENDORSER, address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, address)).to.equal(true)

      // revoke TRUSTEE role
      await roleControl.connect(testAccounts.trustee.account).revokeRole(ROLES.ENDORSER, address)
      expect(await roleControl.hasRole(ROLES.ENDORSER, address)).to.equal(false)
    })

    it('should fail when revoke ENDORSER role by an account without any role', async function () {
      await expect(
        roleControl.connect(testAccounts.noRole.account).revokeRole(ROLES.ENDORSER, testAccounts.endorser.account),
      ).to.be.rejectedWith(
        Error,
        "VM Exception while processing transaction: reverted with reason string 'Sender does not have required role to perform action",
      )
    })
  })
})
