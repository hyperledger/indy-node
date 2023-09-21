import chai from 'chai'
import { RoleControl, ValidatorControl } from '../../contracts-ts'
import { Account } from '../../utils'
import { getTestAccounts, TestAccounts, ZERO_ADDRESS } from '../utils'

const { expect } = chai

describe('ValidatorControl', function () {
  let roleControl: RoleControl
  let validatorControl: ValidatorControl
  let testAccounts: TestAccounts

  const validator1: string = new Account().address
  const validator2: string = new Account().address
  const initialValidators: Array<string> = [validator1, validator2]

  beforeEach('deploy ValidatorSmartContract', async () => {
    roleControl = await new RoleControl().deploy()
    testAccounts = await getTestAccounts(roleControl)
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
