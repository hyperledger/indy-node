import { loadFixture } from '@nomicfoundation/hardhat-network-helpers'
import chai from 'chai'
import { RoleControl } from '../../contracts-ts'
import { Account } from '../../utils'
import { TestableValidatorControl } from '../utils/contract-helpers'
import { AuthErrors, ValidatorControlErrors } from '../utils/errors'
import { getTestAccounts, ZERO_ADDRESS } from '../utils/test-entities'

const { expect } = chai

describe('ValidatorControl', function () {
  const validator1: string = new Account().address
  const validator2: string = new Account().address
  const initialValidators: Array<string> = [validator1, validator2]

  async function deployValidatorControlFixture() {
    const roleControl = await new RoleControl().deployProxy({ params: [ZERO_ADDRESS] })
    const testAccounts = await getTestAccounts(roleControl)

    const initialValidatorsData = [
      {
        validator: validator1,
        account: testAccounts.steward.account.address,
      },
      {
        validator: validator2,
        account: testAccounts.steward2.account.address,
      },
    ]

    const validatorControl = await new TestableValidatorControl().deployProxy({
      params: [roleControl.address, ZERO_ADDRESS, initialValidatorsData],
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
      ).to.revertedWithCustomError(validatorControl.baseInstance, ValidatorControlErrors.InvalidValidatorAddress)
    })

    it('should fail when adding duplicate validator address', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await expect(validatorControl.connect(testAccounts.steward3.account).addValidator(validator1))
        .to.revertedWithCustomError(validatorControl.baseInstance, ValidatorControlErrors.ValidatorAlreadyExists)
        .withArgs(validator1)
    })

    it('should fail when adding second validator address', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await validatorControl.connect(testAccounts.steward3.account).addValidator(newValidator.address)

      await expect(validatorControl.connect(testAccounts.steward3.account).addValidator(new Account().address))
        .to.revertedWithCustomError(validatorControl.baseInstance, ValidatorControlErrors.SenderHasActiveValidator)
        .withArgs(testAccounts.steward3.account.address)
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
      ).to.be.revertedWithCustomError(
        validatorControl.baseInstance,
        ValidatorControlErrors.CannotDeactivateLastValidator,
      )

      await validatorControl.connect(testAccounts.steward2.account).addValidator(validator2)
    })

    it('should fail when delete not exising validator', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      const notExisingValidator = new Account()
      await expect(validatorControl.connect(testAccounts.steward.account).removeValidator(notExisingValidator.address))
        .to.revertedWithCustomError(validatorControl.baseInstance, ValidatorControlErrors.ValidatorNotFound)
        .withArgs(notExisingValidator.address)
    })

    it('should fail when trying to delete a validator with zero address', async function () {
      const { validatorControl, testAccounts } = await loadFixture(deployValidatorControlFixture)

      await expect(
        validatorControl.connect(testAccounts.steward.account).removeValidator(ZERO_ADDRESS),
      ).to.revertedWithCustomError(validatorControl.baseInstance, ValidatorControlErrors.InvalidValidatorAddress)
    })
  })
})
