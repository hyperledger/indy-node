"""
Created on Nov 8, 2017

@author: nhan.nguyen

Containing test script of test scenario 09: remove and add role.
"""
import json
import sys
import os
from indy import ledger, signus
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from libraries.constant import Constant, Colors, Roles
from libraries.result import Status
from libraries.common import Common
from libraries import utils
from test_scripts.test_scenario_base import TestScenarioBase


class TestScenario09(TestScenarioBase):

    async def execute_test_steps(self):
        """
        This function is the main part of test script.
        All steps that involve to role TGB (9, 10, a half of 24) will be skipped because
        role TGB is not supported by libindy.
        There is a bug in this scenario (in step 22, 23 24) so we log a bug here.
        """
        try:
            # 1. Create and open wallet, pool ledger.
            self.steps.add_step("Create and open wallet, pool ledger")
            result = await utils.perform(self.steps, Common.prepare_pool_and_wallet,
                                         self.pool_name, self.wallet_name, Constant.pool_genesis_txn_file)
            utils.raise_if_exception(result)
            (self.pool_handle, self.wallet_handle) = result

            # 2. Create DIDs.
            self.steps.add_step("Create DIDs")

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({"seed": Constant.seed_default_trustee}))
            (default_trustee_did, default_trustee_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (trustee1_did, trustee1_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (trustee2_did, trustee2_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (steward1_did, steward1_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (steward2_did, steward2_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (steward3_did, steward3_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (trustanchor1_did, trustanchor1_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (trustanchor2_did, trustanchor2_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (trustanchor3_did, trustanchor3_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (user1_did, user1_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (user3_did, user3_verkey) = result if len(result) == 2 else (None, None)

            result = await utils.perform(self.steps, signus.create_and_store_my_did,
                                         self.wallet_handle, json.dumps({}))
            (user4_did, user4_verkey) = result if len(result) == 2 else (None, None)

            # ==========================================================================================================
            # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # ==========================================================================================================

            # 3. Using default Trustee to create Trustee1.
            self.steps.add_step("Using default Trustee to create Trustee1")
            await self.add_nym(default_trustee_did, trustee1_did, trustee1_verkey, None, Roles.TRUSTEE)

            # 4. Verify GET NYM - Trustee1.
            self.steps.add_step("Verify GET NYM - Trustee1")
            await self.get_nym(default_trustee_did, trustee1_did)

            # 5. Using Trustee1 to create Steward1.
            self.steps.add_step("Using Trustee1 to create Steward1")
            await self.add_nym(trustee1_did, steward1_did, steward1_verkey, None, Roles.STEWARD)

            # 6. Verify GET NYM - Steward1.
            self.steps.add_step("Verify GET NYM - Steward1")
            await self.get_nym(trustee1_did, steward1_did)

            # 7. Add identity (no role) by Trustee1.
            self.steps.add_step("Add identity (no role) by Trustee1")
            await self.add_nym(trustee1_did, user3_did, user3_verkey, None, None)

            # 8. Verify GET NYM - no role.
            self.steps.add_step("Verify GET NYM - no role")
            await self.get_nym(trustee1_did, user3_did)

            # Role TGB is not exist so we do not execute step 9.
            # 9. Using Trustee1 to create a TGB role.
            self.steps.add_step("Using Trustee1 to create a TGB role (SKIP)")
            self.steps.get_last_step().set_status(Status.PASSED)

            # Role TGB is not exist so we do not execute step 12.
            # 10. Verify GET NYM - TGB1.
            self.steps.add_step("Verify GET NYM - TGB1 (SKIP)")
            self.steps.get_last_step().set_status(Status.PASSED)

            # 11. Using Steward1 to create TrustAnchor1.
            self.steps.add_step("Using Steward1 to create TrustAnchor1")
            await self.add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey, None, Roles.TRUST_ANCHOR)

            # 12. Verify GET NYM - TrustAnchor1.
            self.steps.add_step("Verify GET NYM - TrustAnchor1")
            await self.get_nym(steward1_did, trustanchor1_did)

            # 13. Verify add identity (no role) by Steward1.
            self.steps.add_step("Verify add identity (no role) by Steward1")
            await self.add_nym(steward1_did, user4_did, user4_verkey, None, None)

            # 14. Verify GET NYM.
            self.steps.add_step("Verify GET NYM - no role")
            await self.get_nym(steward1_did, user4_did)

            # 15. Verify that a Steward cannot create another Steward.
            self.steps.add_step("Verify that Steward cannot create another Steward")
            (temp, message) = await self.add_nym(steward1_did, steward2_did, steward2_verkey, None,
                                                 Roles.STEWARD, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Steward!\n" + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward can create another Steward (should fail)"
                self.steps.get_last_step().set_message(message)

            # 16. Verify that a Steward cannot create a Trustee.
            self.steps.add_step("Verify that a Steward cannot create a Trustee")
            (temp, message) = await self.add_nym(steward1_did, trustee1_did, trustee1_verkey,
                                                 None, Roles.TRUSTEE, error_code=304)

            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Trustee!\n" + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward can create a Trustee (should fail)"
                self.steps.get_last_step().set_message(message)

            # 17. Using TrustAnchor1 to add a NYM.
            self.steps.add_step("Using TrustAnchor1 to add a NYM")
            await self.add_nym(trustanchor1_did, user1_did, user1_verkey, None, None)

            # 18. Verify GET NYM - User1.
            self.steps.add_step("Verify GET NYM - User1")
            await self.get_nym(trustanchor1_did, user1_did)

            # 19. Verify that TrustAnchor cannot create another TrustAnchor.
            self.steps.add_step("Verify that TrustAnchor cannot create another TrustAnchor")
            (temp, message) = await self.add_nym(trustanchor1_did, trustanchor2_did, trustanchor2_verkey,
                                                 None, Roles.TRUST_ANCHOR, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that a TrustAnchor cannot create another TrustAnchor!\n"
                      + Colors.ENDC)
            else:
                if message is None:
                    message = "TrustAnchor can create another TrustAnchor (should fail)"
                self.steps.get_last_step().set_message(message)

            # 20. Using default Trustee to remove new roles.
            bug_is_430 = "Bug: https://jira.hyperledger.org/browse/IS-430"
            self.steps.add_step("Using default Trustee to remove new roles")
            message_20 = ""
            (temp, message) = await self.add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                 None, Roles.NONE)
            result = temp
            if not temp:
                message_20 += "\nCannot remove Trustee1's role - " + message
            else:
                (temp, message) = await self.get_nym(default_trustee_did, trustee1_did)
                if not temp:
                    message_20 += "\nCannot check self.get_nym for Trustee1 - " + message
                else:
                    if not TestScenario09.check_role_in_retrieved_nym(message, Roles.NONE):
                        temp = False
                        message_20 += "\nCannot remove Trustee1's role"

            result = result and temp
            (temp, message) = await self.add_nym(default_trustee_did, steward1_did, steward1_verkey,
                                                 None, Roles.NONE)
            result = result and temp
            if not temp:
                message_20 += "\nCannot remove Steward1's role - " + message
            else:
                (temp, message) = await self.get_nym(default_trustee_did, steward1_did)
                if not temp:
                    message_20 += "\nCannot check self.get_nym for Steward1 - " + message
                else:
                    if not TestScenario09.check_role_in_retrieved_nym(message, Roles.NONE):
                        temp = False
                        message_20 += "\nCannot remove Steward1's role"

            result = result and temp

            (temp, message) = await self.add_nym(default_trustee_did, trustanchor1_did,
                                                 trustanchor1_verkey, None, Roles.NONE)
            result = result and temp

            if not temp:
                message_20 += "\nCannot remove Trust_Anchor1's role - " + message
            else:
                (temp, message) = await self.get_nym(default_trustee_did, trustanchor1_did)
                if not temp:
                    message_20 += "\nCannot check self.get_nym for Trust_Anchor1 - " + message
                else:
                    if not TestScenario09.check_role_in_retrieved_nym(message, Roles.NONE):
                        temp = False
                        message_20 += "\nCannot remove Trust_Anchor1's role"

            result = result and temp

            if not result:
                self.steps.get_last_step().set_message("{}\n{}".format(message_20[1:], bug_is_430))
                self.steps.get_last_step().set_status(Status.FAILED)
            else:
                self.steps.get_last_step().set_status(Status.PASSED)

            # 21. Verify that removed Trustee1 cannot create Trustee or Steward.
            self.steps.add_step("Verify that removed Trustee1 cannot create Trustee or Steward")
            message_21 = ""
            (temp, message) = await self.add_nym(trustee1_did, trustee2_did, trustee2_verkey,
                                                 None, Roles.TRUSTEE, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create another Trustee!\n"
                      + Colors.ENDC)
            else:
                if message is None:
                    message = ""
                message_21 += "\nRemoved Trustee can create Trustee (should fail) " + message

            result = temp

            (temp, message) = await self.add_nym(trustee1_did, steward2_did, steward2_verkey,
                                                 None, Roles.STEWARD, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create a Steward!\n"
                      + Colors.ENDC)
            else:
                if message is None:
                    message = ""
                message_21 += "\nRemoved Trustee can create Steward(should fail) " + message

            result = result and temp

            if not result:
                self.steps.get_last_step().set_message("{}\n{}".format(message_21[1:], bug_is_430))
                self.steps.get_last_step().set_status(Status.FAILED)
            else:
                self.steps.get_last_step().set_status(Status.PASSED)

            # 22. Verify that removed Steward1 cannot create TrustAnchor.
            self.steps.add_step("Verify that removed Steward1 cannot create TrustAnchor")
            (temp, message) = await self.add_nym(steward1_did, trustanchor2_did, trustanchor2_verkey,
                                                 None, Roles.TRUST_ANCHOR, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that removed Steward1 cannot create a TrustAnchor!\n"
                      + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward1 can create a TrustAnchor (should fail)"
                self.steps.get_last_step().set_message("{}\n{}".format(message, bug_is_430))

            # 23. Using default Trustee to create Trustee1.
            self.steps.add_step("Using default Trustee to create Trustee1")
            await self.add_nym(default_trustee_did, trustee1_did, trustee1_verkey, None, Roles.TRUSTEE)

            # 24. Using Trustee1 to add Steward1.
            self.steps.add_step("Using Trustee1 to add Steward1")
            await self.add_nym(trustee1_did, steward1_did, steward1_verkey, None, Roles.STEWARD)

            # 25. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee.
            self.steps.add_step("Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee")
            (temp, message) = await self.add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                                 None, Roles.TRUST_ANCHOR, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that Steward1 cannot add "
                                       "back a TrustAnchor removed by TrustTee!\n"
                      + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward1 can add back TrustAnchor removed by Trustee (should fail)"
                self.steps.get_last_step().set_message(message)

            # 26. Verify that Steward cannot remove a Trustee.
            self.steps.add_step("Verify that Steward cannot remove a Trustee")
            (temp, message) = await self.add_nym(steward1_did, trustee1_did, trustee1_verkey,
                                                 None, Roles.NONE, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove a Trustee!\n" + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward can create a Trustee (should fail)"
                self.steps.get_last_step().set_message(message)

            # 27. Verify that Trustee can add new Steward.
            self.steps.add_step("Verify that Trustee can add new Steward")
            message_27 = ""
            (temp, message) = await self.add_nym(trustee1_did, steward2_did, steward2_verkey, None, Roles.STEWARD)
            result = temp
            if not temp:
                message_27 += "\nTrustee cannot add Steward1 (should pass) - " + message

            (temp, message) = await self.add_nym(trustee1_did, steward3_did, steward3_verkey, None, Roles.STEWARD)
            result = result and temp
            if not temp:
                message_27 += "\nTrustee cannot add Steward2 (should pass) - " + message

            if not result:
                self.steps.get_last_step().set_status(Status.FAILED)
                self.steps.get_last_step().set_message(message_27[1:])
            else:
                self.steps.get_last_step().set_status(Status.PASSED)

            # 28. Verify that Steward cannot remove another Steward.
            self.steps.add_step("Verify that Steward cannot remove another Steward")
            (temp, message) = await self.add_nym(steward1_did, steward2_did, steward2_verkey, None,
                                                 Roles.NONE, error_code=304)
            if temp:
                print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove another Steward!\n" + Colors.ENDC)
            else:
                if message is None:
                    message = "Steward can remove another Steward (should fail)"
                    self.steps.get_last_step().set_message(message)

            # 29. Verify Steward can add a TrustAnchor.
            self.steps.add_step("Verify Steward can add a TrustAnchor")
            await self.add_nym(steward2_did, trustanchor3_did, trustanchor3_verkey, None, Roles.TRUST_ANCHOR)
        except Exception as e:
            print(Colors.FAIL + "\n\t{}\n".format(str(e)) + Colors.ENDC)

    async def add_nym(self, submitter_did, target_did, ver_key, alias, role, error_code=None):
        """
        Build a send NYM request and submit it.

        :param submitter_did: (optional) DID of request submitter
        :param target_did: (optional) DID of request target
        :param ver_key: (optional) ver_key of request target
        :param alias: (optional)
        :param role: (optional) role
        :param error_code: the error_code that you expect
        :return: (True, message) if send NYM successfully (message is result of send NYM).
                 (False, message) if send NYM failed (message is result of send NYM)
        """
        nym = await utils.perform(self.steps, ledger.build_nym_request, submitter_did, target_did, ver_key, alias, role)
        if isinstance(nym, IndexError or Exception):
            return False, None

        if not error_code:
            result = await utils.perform(self.steps, ledger.sign_and_submit_request, self.pool_handle,
                                         self.wallet_handle, submitter_did, nym)
            if isinstance(result, IndexError or Exception):
                return False, result
            return True, None
        else:
            result = await utils.perform_with_expected_code(self.steps, ledger.sign_and_submit_request,
                                                            self.pool_handle, self.wallet_handle, submitter_did, nym,
                                                            expected_code=error_code)
            if self.steps.get_last_step().get_status() == Status.FAILED:
                return False, result
            return True, None

    async def get_nym(self, submitter_did, target_did):
        """
        Build and submit GET NYM request.

        :param submitter_did: (optional) DID of request submitter.
        :param target_did: (optional) DID of request target.
        :return: (True, message) if GET_NYM is sent successfully (message is result of GET_NYM).
                 (False, message) if GET_NYM cannot be sent (message is result of GET_NYM)
        """

        nym = await utils.perform(self.steps, ledger.build_get_nym_request, submitter_did, target_did)
        if isinstance(nym, IndexError or Exception):
            return False, None
        result = await  utils.perform(self.steps, ledger.submit_request, self.pool_handle, nym)
        if isinstance(result, IndexError or Exception):
            return False, result
        return True, result

    @staticmethod
    def check_role_in_retrieved_nym(retrieved_nym, role):
        """
        Check if the role in the GET NYM response is what we want.

        :param retrieved_nym:
        :param role: the role we want to check.
        :return: True if the role is what we want.
                 False if the role is not what we want.
        """
        if retrieved_nym is None:
            return False
        nym_dict = json.loads(retrieved_nym)
        if "data" in nym_dict["result"]:
            temp_dict = json.loads(nym_dict["result"]["data"])
            if "role" in temp_dict:
                if not temp_dict["role"] == role:
                    return False
                else:
                    return True
        return False


if __name__ == '__main__':
    TestScenario09().execute_scenario()
