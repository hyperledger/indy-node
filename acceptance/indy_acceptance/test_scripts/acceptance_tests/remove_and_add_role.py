"""
Created on Nov 8, 2017

@author: nhan.nguyen

Containing test script of test scenario 09: remove and add role.
"""
import json

from indy import ledger, signus

from indy_acceptance.utilities import common
from indy_acceptance.utilities.constant import pool_genesis_txn_file, \
                                                seed_default_trustee
from indy_acceptance.utilities import utils
from indy_acceptance.utilities.constant import Color, Role
from indy_acceptance.utilities.result import Status
from indy_acceptance.test_scripts.test_scenario_base import TestScenarioBase


class RemoveAndAddRole(TestScenarioBase):
    async def execute_test_steps(self):
        """
        This function is the main part of test script.
        All steps that involve to role TGB(9, 10, a half of 24) will be skipped
        because role TGB is not supported by libindy.
        There is a bug in this scenario(in step 22, 23 24) so we log a bug here
        """
        # 1. Create and open wallet, pool ledger.
        self.steps.add_step("Create and open wallet, pool ledger")
        self.pool_handle, self.wallet_handle = await utils.perform(
            self.steps,
            common.prepare_pool_and_wallet,
            self.pool_name,
            self.wallet_name,
            pool_genesis_txn_file,
            ignore_exception=False)

        # 2. Create DIDs.
        self.steps.add_step("Create DIDs")

        (default_trustee_did, _) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle,
            json.dumps({"seed": seed_default_trustee}))

        (trustee1_did, trustee1_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (trustee2_did, trustee2_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (steward1_did, steward1_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (steward2_did, steward2_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (steward3_did, steward3_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (trustanchor1_did, trustanchor1_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (trustanchor2_did, trustanchor2_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (trustanchor3_did, trustanchor3_verkey) = await utils.perform(
            self.steps,
            signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (user1_did, user1_verkey) = await utils.perform(
            self.steps, signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (user3_did, user3_verkey) = await utils.perform(
            self.steps, signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        (user4_did, user4_verkey) = await utils.perform(
            self.steps, signus.create_and_store_my_did,
            self.wallet_handle, json.dumps({}))

        # =====================================================================
        # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # =====================================================================

        # 3. Using default Trustee to create Trustee1.
        self.steps.add_step("Using default Trustee to create Trustee1")
        await self.add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                           None, Role.TRUSTEE)

        # 4. Verify GET NYM - Trustee1.
        self.steps.add_step("Verify GET NYM - Trustee1")
        await self.get_nym(default_trustee_did, trustee1_did)

        # 5. Using Trustee1 to create Steward1.
        self.steps.add_step("Using Trustee1 to create Steward1")
        await self.add_nym(trustee1_did, steward1_did, steward1_verkey, None,
                           Role.STEWARD)

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
        await self.add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                           None, Role.TRUST_ANCHOR)

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
        self.steps.add_step(
            "Verify that Steward cannot create another Steward")
        error_msg = "Steward can create another Steward (should fail)"
        successful_msg = "::PASS::Validated that a Steward " \
                         "cannot create a Steward!\n"

        (temp, message) = await self.add_nym(steward1_did, steward2_did,
                                             steward2_verkey, None,
                                             Role.STEWARD, error_code=304,
                                             default_message=error_msg)

        self.check(temp, successful_msg, message)

        # 16. Verify that a Steward cannot create a Trustee.
        self.steps.add_step("Verify that a Steward cannot create a Trustee")
        error_msg = "Steward can create a Trustee (should fail)"
        successful_msg = "::PASS::Validated that a Steward " \
                         "cannot create a Trustee!\n"

        (temp, message) = await self.add_nym(steward1_did, trustee1_did,
                                             trustee1_verkey,
                                             None, Role.TRUSTEE,
                                             error_code=304,
                                             default_message=error_msg)

        self.check(temp, successful_msg, message)

        # 17. Using TrustAnchor1 to add a NYM.
        self.steps.add_step("Using TrustAnchor1 to add a NYM")
        await self.add_nym(trustanchor1_did, user1_did, user1_verkey,
                           None, None)

        # 18. Verify GET NYM - User1.
        self.steps.add_step("Verify GET NYM - User1")
        await self.get_nym(trustanchor1_did, user1_did)

        # 19. Verify that TrustAnchor cannot create another TrustAnchor.
        self.steps.add_step(
            "Verify that TrustAnchor cannot create another TrustAnchor")
        error_msg = "TrustAnchor can create another TrustAnchor (should fail)"
        successful_msg = "::PASS::Validated that a TrustAnchor" \
                         " cannot create another TrustAnchor!\n"
        (temp, message) = await self.add_nym(trustanchor1_did,
                                             trustanchor2_did,
                                             trustanchor2_verkey,
                                             None, Role.TRUST_ANCHOR,
                                             error_code=304,
                                             default_message=error_msg)
        self.check(temp, successful_msg, message)

        # 20. Using default Trustee to remove new roles.
        bug_is_430 = "Bug: https://jira.hyperledger.org/browse/IS-430"
        self.steps.add_step("Using default Trustee to remove new roles")
        message_20 = ""
        (temp, message) = await self.remove_role_and_check(default_trustee_did,
                                                           trustee1_did,
                                                           trustee1_verkey,
                                                           None, "Trustee1")
        result = temp
        message_20 += message

        (temp, message) = await self.remove_role_and_check(default_trustee_did,
                                                           steward1_did,
                                                           steward1_verkey,
                                                           None, "Steward1")
        result = result and temp
        message_20 += message

        (temp, message) = await self.remove_role_and_check(default_trustee_did,
                                                           trustanchor1_did,
                                                           trustanchor1_verkey,
                                                           None,
                                                           "TrustAnchor1")
        result = result and temp
        message_20 += message

        if not result:
            self.steps.get_last_step().set_message(
                "{}\n{}".format(message_20[1:], bug_is_430))
            self.steps.get_last_step().set_status(Status.FAILED)
        else:
            self.steps.get_last_step().set_status(Status.PASSED)

        # 21. Verify that removed Trustee1 cannot create Trustee or Steward.
        self.steps.add_step(
            "Verify that removed Trustee1 cannot create Trustee or Steward")
        (temp, message) = await self.add_nym(trustee1_did, trustee2_did,
                                             trustee2_verkey, None,
                                             Role.TRUSTEE, error_code=304)

        error_msg = "\nRemoved Trustee can create Trustee  (should fail) "
        successful_msg = "::PASS::Validated that removed Trustee1 " \
                         "cannot create another Trustee!\n"
        self.check(temp, successful_msg, error_msg[1:] + message)
        result = temp

        (temp, message) = await self.add_nym(trustee1_did, steward2_did,
                                             steward2_verkey, None,
                                             Role.STEWARD, error_code=304)

        successful_msg = "::PASS::Validated that removed Trustee1 " \
                         "cannot create a Steward!\n"
        error_msg = "\nRemoved Trustee can create Steward (should fail) "

        self.check(temp, successful_msg, "{}{}\n{}".format(error_msg[1:],
                                                           message,
                                                           bug_is_430))
        result = result and temp

        if not result:
            self.steps.get_last_step().set_status(Status.FAILED)
        else:
            self.steps.get_last_step().set_status(Status.PASSED)

        # 22. Verify that removed Steward1 cannot create TrustAnchor.
        self.steps.add_step(
            "Verify that removed Steward1 cannot create TrustAnchor")
        default_msg = "Steward1 can create a TrustAnchor (should fail)"
        successful_msg = "::PASS::Validated that removed Steward1 " \
                         "cannot create a TrustAnchor!\n"
        (temp, message) = await self.add_nym(steward1_did, trustanchor2_did,
                                             trustanchor2_verkey, None,
                                             Role.TRUST_ANCHOR, error_code=304,
                                             default_message=default_msg)
        error_msg = "{}\n{}".format(message, bug_is_430)
        self.check(temp, successful_msg, error_msg)

        # 23. Using default Trustee to create Trustee1.
        self.steps.add_step("Using default Trustee to create Trustee1")
        await self.add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                           None, Role.TRUSTEE)

        # 24. Using Trustee1 to add Steward1.
        self.steps.add_step("Using Trustee1 to add Steward1")
        await self.add_nym(trustee1_did, steward1_did, steward1_verkey,
                           None, Role.STEWARD)

        # 25. Verify that Steward1 cannot add back a TrustAnchor removed by
        # TrustTee.
        self.steps.add_step(
            "Verify that Steward1 cannot add back a TrustAnchor"
            " removed by TrustTee")
        error_msg = "Steward1 can add back TrustAnchor removed " \
                    "by Trustee (should fail)"
        successful_msg = "::PASS::Validated that Steward1 cannot add" \
                         "back a TrustAnchor removed by TrustTee!\n"

        (temp, message) = await self.add_nym(steward1_did, trustanchor1_did,
                                             trustanchor1_verkey, None,
                                             Role.TRUST_ANCHOR, error_code=304,
                                             default_message=error_msg)
        self.check(temp, successful_msg, message)

        # 26. Verify that Steward cannot remove a Trustee.
        self.steps.add_step("Verify that Steward cannot remove a Trustee")
        error_msg = "Steward can create a Trustee (should fail)"
        successful_msg = "::PASS::Validated that Steward " \
                         "cannot remove a Trustee!\n"
        (temp, message) = await self.add_nym(steward1_did, trustee1_did,
                                             trustee1_verkey, None,
                                             Role.NONE, error_code=304,
                                             default_message=error_msg)
        self.check(temp, successful_msg, message)

        # 27. Verify that Trustee can add new Steward.
        self.steps.add_step("Verify that Trustee can add new Steward")
        message_27 = ""
        (temp, message) = await self.add_nym(trustee1_did, steward2_did,
                                             steward2_verkey, None,
                                             Role.STEWARD)
        result = temp
        if not temp:
            message_27 += "\nTrustee cannot add Steward1 (should pass) - " + \
                          message

        (temp, message) = await self.add_nym(trustee1_did, steward3_did,
                                             steward3_verkey, None,
                                             Role.STEWARD)
        result = result and temp
        if not temp:
            message_27 += "\nTrustee cannot add Steward2 (should pass) - " + \
                          message

        if not result:
            self.steps.get_last_step().set_status(Status.FAILED)
            self.steps.get_last_step().set_message(message_27[1:])
        else:
            self.steps.get_last_step().set_status(Status.PASSED)

        # 28. Verify that Steward cannot remove another Steward.
        self.steps.add_step(
            "Verify that Steward cannot remove another Steward")
        error_msg = "Steward can remove another Steward (should fail)"
        successful_msg = "::PASS::Validated that Steward " \
                         "cannot remove another Steward!\n"
        (temp, message) = await self.add_nym(steward1_did, steward2_did,
                                             steward2_verkey, None,
                                             Role.NONE, error_code=304)
        self.check(temp, successful_msg, error_msg)

        # 29. Verify Steward can add a TrustAnchor.
        self.steps.add_step("Verify Steward can add a TrustAnchor")
        await self.add_nym(steward2_did, trustanchor3_did, trustanchor3_verkey,
                           None, Role.TRUST_ANCHOR)

    async def add_nym(self, submitter_did, target_did, ver_key, alias, role,
                      error_code=None, default_message: str = ""):
        """
        Build a send NYM request and submit it.

        :param submitter_did: DID of request submitter
        :param target_did: DID of request target
        :param ver_key: ver_key of request target
        :param alias:
        :param role: role
        :param error_code: (optional) the error_code that you expect
        :param default_message: (optional)
                                 if there is no message, return default message
        :return: (True, message) if send NYM successfully
                                 (message is result of send NYM).
                 (False, message) if send NYM failed
                                 (message is result of send NYM)
        """
        nym = await utils.perform(self.steps, ledger.build_nym_request,
                                  submitter_did, target_did, ver_key,
                                  alias, role)
        if isinstance(nym, Exception):
            return False, str(nym)

        if not error_code:
            result = await utils.perform(
                self.steps, ledger.sign_and_submit_request,
                self.pool_handle, self.wallet_handle,
                submitter_did, nym)

            if isinstance(result, Exception):
                return False, str(result)
            return True, ""
        else:
            await utils.perform_with_expected_code(
                self.steps, ledger.sign_and_submit_request,
                self.pool_handle, self.wallet_handle, submitter_did,
                nym, expected_code=error_code)

            if self.steps.get_last_step().get_status() == Status.FAILED:
                return False, default_message
            return True, ""

    async def get_nym(self, submitter_did, target_did):
        """
        Build and submit GET NYM request.

        :param submitter_did: DID of request submitter.
        :param target_did: DID of request target.
        :return: (True, message) if GET_NYM is sent successfully
                                 (message is result of GET_NYM).
                 (False, message) if GET_NYM cannot be sent
                                  (message is result of GET_NYM)
        """

        nym = await utils.perform(self.steps, ledger.build_get_nym_request,
                                  submitter_did, target_did)
        if isinstance(nym, Exception):
            return False, None
        result = await  utils.perform(self.steps, ledger.submit_request,
                                      self.pool_handle, nym)
        if isinstance(result, Exception):
            return False, result
        return True, result

    async def remove_role_and_check(self, submitter_did, target_did,
                                    target_verkey, alias, target_name):
        """
        Remove role and get NYM to check that role is removed successfully.

        :param submitter_did:
        :param target_did:
        :param target_verkey:
        :param alias:
        :param target_name: name of targer (like Trustee1, Steward1,...)
        :return: result of removing role and message
        """
        (temp, temp_msg) = await self.add_nym(submitter_did, target_did,
                                              target_verkey, alias, Role.NONE)

        message = ""
        if not temp:
            message = "\nCannot remove {}'s role - {}".format(target_name,
                                                              temp_msg)
        else:
            (temp, temp_msg) = await self.get_nym(submitter_did, target_did)
            if not temp:
                message += "\nCannot get NYM for{} - {}".format(target_name,
                                                                temp_msg)
            else:
                if not RemoveAndAddRole.check_role_in_retrieved_nym(temp_msg,
                                                                    Role.NONE):
                    temp = False
                    message += "\nCannot remove {}'s role".format(target_name)

        return temp, message

    def check(self, result: bool, successful_msg: str, error_msg: str):
        """
        Check whether result True or False.
        If result is False then setting error message for last step
        else print successful message

        :param result: condition
        :param successful_msg: successful message.
        :param error_msg: error message.
        :return:
        """
        if result:
            if successful_msg:
                utils.print_with_color(successful_msg, Color.OKGREEN)
        else:
            if error_msg:
                step = self.steps.get_last_step()
                temp_msg = "" if not step.get_message() else step.get_message()
                temp_msg = "{}\n{}".format(temp_msg, error_msg)
                step.set_message(temp_msg)

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
    RemoveAndAddRole().execute_scenario()
