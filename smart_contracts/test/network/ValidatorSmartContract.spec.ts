import { ethers } from "hardhat";

import chai from "chai";
import { getTestAccounts, TestAccounts, web3 } from "../utils";

const {expect} = chai;

describe('ValidatorSmartContract', () => {
    let roleControl: any
    let validatorControl: any
    let validatorAddress: string
    let testAccounts: TestAccounts
    let initialValidators: Array<String>

    before('deploy ValidatorSmartContract', async () => {
        testAccounts = await getTestAccounts()
        roleControl = await ethers.deployContract('RoleControl', [ Object.values(testAccounts) ])
        validatorAddress = web3.eth.accounts.create().address
        initialValidators = [ validatorAddress ]
        const initialValidatorsData = [
            {
                validator: validatorAddress,
                account: testAccounts.steward.account
            }
        ]
        validatorControl =
            await ethers.deployContract(
                'ValidatorsControl',
                [ await roleControl.getAddress(), initialValidatorsData ]
            )
    })

    describe('getValidators', () => {
        it("should return the list of current validators", async function () {
            const validators = await validatorControl.getValidators()
            expect([ ...validators ]).to.have.members([ ...initialValidators ])
        });
    })

    describe('getValidators', () => {
        it("should add a new validator by Steward", async function () {
            const newValidator = web3.eth.accounts.create()
            await validatorControl.connect(testAccounts.steward.account).addValidator(newValidator.address)

            const validators = await validatorControl.getValidators()
            expect(validators.length).to.be.equal(2)
            expect(validators).to.include(newValidator.address)
        });

        it("should fail when adding a new validator by an account without Steward role", async function () {
            const newValidator = web3.eth.accounts.create()

            await expect(
                validatorControl
                    .connect(testAccounts.noRole.account)
                    .addValidator(newValidator.address)
            )
                .to.be.rejectedWith(
                    Error,
                    'VM Exception while processing transaction: reverted with reason string \'Sender does not have STEWARD role assigned\''
                );
        });

        it("should fail when adding duplicate validator address", async function () {
            await expect(
                validatorControl
                    .connect(testAccounts.steward.account)
                    .addValidator(validatorAddress)
            )
                .to.be.rejectedWith(
                    Error,
                    'VM Exception while processing transaction: reverted with reason string \'Validator already exists\''
                );
        });
    })
})
