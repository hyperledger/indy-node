import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import { expect } from 'chai'
import { AccountControl, RoleControl } from '../../contracts-ts'
import {
  createContractDeployTransaction,
  createWriteTransaction,
  getTestAccounts,
  ZERO_ADDRESS,
} from '../utils/test-entities'

describe('AccountControl', function () {
  async function deployAccountControlFixture() {
    const roleControl = await new RoleControl().deployProxy({ params: [ZERO_ADDRESS] })

    const testAccounts = await getTestAccounts(roleControl)

    const accountControl = await new AccountControl().deployProxy({ params: [roleControl.address, ZERO_ADDRESS] })

    return { accountControl, testAccounts }
  }

  describe('transactionAllowed', () => {
    it('Should allow write transaction to sender with trustee role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createWriteTransaction(testAccounts.trustee.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow write transaction to sender with endorser role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createWriteTransaction(testAccounts.endorser.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow write transaction to sender with steward role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createWriteTransaction(testAccounts.steward.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should allow deploy contract to sender with trustee role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createContractDeployTransaction(testAccounts.trustee.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.true
    })

    it('Should not allow deploy contract to sender with endorser role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createContractDeployTransaction(testAccounts.endorser.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.false
    })

    it('Should not allow deploy contract to sender with steward role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const transaction = createContractDeployTransaction(testAccounts.steward.account.address)

      expect(await accountControl.transactionAllowed(transaction)).to.be.false
    })

    it('Should not allow write any transaction to sender without role', async function () {
      const { accountControl, testAccounts } = await loadFixture(deployAccountControlFixture)

      const deployTransaction = createContractDeployTransaction(testAccounts.noRole.account.address)
      const writeTransaction = createWriteTransaction(testAccounts.noRole.account.address)

      expect(await accountControl.transactionAllowed(deployTransaction)).to.be.false
      expect(await accountControl.transactionAllowed(writeTransaction)).to.be.false
    })
  })
})
