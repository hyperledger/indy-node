import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import chai from 'chai'
import { RoleControl, ValidatorControl } from '../../contracts-ts'
import { Account } from '../../utils'
import { TestableValidatorControl } from '../utils/contract-helpers'
import { AuthErrors } from '../utils/errors'
import { getTestAccounts, ZERO_ADDRESS } from '../utils/test-entities'

const { expect } = chai

describe('ValidatorControl', function () {
  const validator1: string = new Account().address
  const validator2: string = new Account().address
  const initialValidators: Array<string> = [validator1, validator2]

  async function deployValidatorControlFixture() {
    const roleControl = await new RoleControl().deploy()
    const testAccounts = await getTestAccounts(roleControl)

    const initialValidatorsData = [
      {
        validator: validator1,
        account: testAccounts.steward.account,
      },
      {
        validator: validator2,
        account: testAccounts.steward2.account,
      },
    ]

    const validatorControl = await new TestableValidatorControl().deploy({
      params: [roleControl.address, initialValidatorsData],
    })

    return { validatorControl, roleControl, testAccounts }
  }

  describe('getValidators', () => {
    it('should return the list of current validators', async function () {
      const { validatorControl } = await loadFixture(deployValidatorControlFixture)

      const validators = await validatorControl.getValidators()
      expect([...validators]).to.have.members([...initialValidators])
    })
  })

  describe('addValidator', () => {
    const newValidator = new Account()

    it('should add a new validator by Steward', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await validatorControl.connect(testAccounts.steward3.account).addValidator(newValidator.address)

      const validators = await validatorControl.getValidators()
      expect(validators.length).to.be.equal(3)
      expect(validators).to.include(newValidator.address)

      await validatorControl.connect(testAccounts.steward3.account).removeValidator(newValidator.address)
    })

    it('should fail when adding a new validator by an account without Steward role', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await expect(validatorControl.connect(testAccounts.noRole.account).addValidator(newValidator.address))
        .to.revertedWithCustomError(validatorControl.baseInstance, AuthErrors.Unauthorized)
        .withArgs(testAccounts.noRole.account.address)
    })

    it('should fail when adding a new validator with zero address', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await expect(
        validatorControl.connect(testAccounts.steward3.account).addValidator(ZERO_ADDRESS),
      ).to.be.revertedWith('Cannot add validator with address 0')
    })

    it('should fail when adding duplicate validator address', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await expect(validatorControl.connect(testAccounts.steward3.account).addValidator(validator1)).to.be.revertedWith(
        'Validator already exists',
      )
    })
  })

  describe('removeValidator', () => {
    it('should remove exising validator by Steward', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      expect((await validatorControl.getValidators()).length).to.be.equal(2)

      const newValidator = new Account().address
      await validatorControl.connect(testAccounts.steward3.account).addValidator(newValidator)
      expect((await validatorControl.getValidators()).length).to.be.equal(3)

      await validatorControl.connect(testAccounts.steward.account).removeValidator(newValidator)

      const validators = await validatorControl.getValidators()
      expect(validators.length).to.be.equal(2)
      expect(validators).not.to.include(newValidator)
      expect(validators).to.include(validator1)
      expect(validators).to.include(validator2)
    })

    it('should fail when delete last validator', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      expect((await validatorControl.getValidators()).length).to.be.equal(2)
      await validatorControl.connect(testAccounts.steward2.account).removeValidator(validator2)
      expect((await validatorControl.getValidators()).length).to.be.equal(1)

      await expect(
        validatorControl.connect(testAccounts.steward.account).removeValidator(validator1),
      ).to.be.revertedWith('Cannot deactivate last validator')

      await validatorControl.connect(testAccounts.steward2.account).addValidator(validator2)
    })

    it('should fail when delete not exising validator', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      const notExisingValidator = new Account()
      await expect(
        validatorControl.connect(testAccounts.steward.account).removeValidator(notExisingValidator.address),
      ).to.be.revertedWith('Validator does not exist')
    })
  })
})
