import chai from 'chai'
import { getTestAccounts, TestAccounts, ZERO_ADDRESS } from '../utils'
import { RoleControl } from '../../contracts-ts/RoleControl'
import { ValidatorControl } from '../../contracts-ts/ValidatorControl'
import { Account } from '../../utils/account'

const { expect } = chai

describe('ValidatorControl', () => {
  let roleControl: RoleControl
  let validatorControl: any
  let validator1: string
  let validator2: string
  let testAccounts: TestAccounts
  let initialValidators: Array<String>

  before('deploy ValidatorSmartContract', async () => {
    roleControl = await new RoleControl().deploy()
    testAccounts = await getTestAccounts(roleControl)
    validator1 = new Account().address
    validator2 = new Account().address
    initialValidators = [validator1, validator2]
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
    validatorControl = await new ValidatorControl().deploy([roleControl.address, initialValidatorsData])
  })

  describe('getValidators', () => {
    it('should return the list of current validators', async function () {
      const validators = await validatorControl.getValidators()
      expect([...validators]).to.have.members([...initialValidators])
    })
  })

  describe('addValidator', () => {
    const newValidator = new Account()

    it('should add a new validator by Steward', async function () {
      await validatorControl.connect(testAccounts.steward3.account).addValidator(newValidator.address)

      const validators = await validatorControl.getValidators()
      expect(validators.length).to.be.equal(3)
      expect(validators).to.include(newValidator.address)

      await validatorControl.connect(testAccounts.steward3.account).removeValidator(newValidator.address)
    })

    it('should fail when adding a new validator by an account without Steward role', async function () {
      const newValidator = new Account()

      await expect(
        validatorControl.connect(testAccounts.noRole.account).addValidator(newValidator.address),
      ).to.be.revertedWith('Sender does not have STEWARD role assigned')
    })

    it('should fail when adding a new validator with zero address', async function () {
      await expect(
        validatorControl.connect(testAccounts.steward3.account).addValidator(ZERO_ADDRESS),
      ).to.be.revertedWith('Cannot add validator with address 0')
    })

    it('should fail when adding duplicate validator address', async function () {
      await expect(validatorControl.connect(testAccounts.steward3.account).addValidator(validator1)).to.be.revertedWith(
        'Validator already exists',
      )
    })
  })

  describe('removeValidator', () => {
    it('should remove exising validator by Steward', async function () {
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
      expect((await validatorControl.getValidators()).length).to.be.equal(2)
      await validatorControl.connect(testAccounts.steward2.account).removeValidator(validator2)
      expect((await validatorControl.getValidators()).length).to.be.equal(1)

      await expect(
        validatorControl.connect(testAccounts.steward.account).removeValidator(validator1),
      ).to.be.revertedWith('Cannot deactivate last validator')

      await validatorControl.connect(testAccounts.steward2.account).addValidator(validator2)
    })

    it('should fail when delete not exising validator', async function () {
      const notExisingValidator = new Account()
      await expect(
        validatorControl.connect(testAccounts.steward.account).removeValidator(notExisingValidator.address),
      ).to.be.revertedWith('Validator does not exist')
    })
  })
})
