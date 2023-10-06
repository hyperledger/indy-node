import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import { AccountControl, RoleControl } from '../../contracts-ts'
import { createContractDeployTransaction, createWriteTransaction, getTestAccounts } from '../utils'
import { expect } from 'chai'

describe('AccountControl', function () {
  async function deployCredDefContractFixture() {
    const roleControl = new RoleControl()
    await roleControl.deploy()

    const testAccounts = await getTestAccounts(roleControl)

    const accountControl = new AccountControl()
    await accountControl.deploy({ params: [roleControl.address] })

    return { accountControl, testAccounts }
  }

  describe('transactionAllowed', () => {

    it('Should allow write transaction to sender with trustee role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createWriteTransaction(testAccounts.trustee.account.address)
      
      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow write transaction to sender with endorser role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createWriteTransaction(testAccounts.endorser.account.address)
      
      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow write transaction to sender with steward role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createWriteTransaction(testAccounts.steward.account.address)
      
      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow deploy contract to sender with trustee role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createContractDeployTransaction(testAccounts.trustee.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should not allow deploy contract to sender with endorser role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createContractDeployTransaction(testAccounts.endorser.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.false
    })

    it('Should not allow deploy contract to sender with steward role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const transaction = createContractDeployTransaction(testAccounts.steward.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.false
    })

    it('Should not allow write any transaction to sender without role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployCredDefContractFixture)

      const deployTransaction = createContractDeployTransaction(testAccounts.noRole.account.address)
      const writeTransaction = createWriteTransaction(testAccounts.noRole.account.address)

      expect(await accountControl.transactionAllowed(deployTransaction)).to.be.false
      expect(await accountControl.transactionAllowed(writeTransaction)).to.be.false
    })
  })
})