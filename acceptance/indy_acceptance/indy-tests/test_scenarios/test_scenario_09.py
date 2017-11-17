import json
import sys
import os
import asyncio
import time
from indy import ledger, pool, signus, wallet
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Constant, Colors, Roles
from utils.report import TestReport, Status
from utils.common import Common
from utils.report import HTMLReport


class MyVars:
    """  Needed some global variables. """

    # Data for creating test report
    test_name = "Test_Scenario_09_Remove_And_Add_Role"
    test_report = TestReport(test_name)
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False, "Step 5": False,
                    "Step 6": False, "Step 7": False, "Step 8": False, "Step 9": False, "Step 10": False,
                    "Step 13": False, "Step 14": False, "Step 15": False, "Step 16": False, "Step 17": False,
                    "Step 18": False, "Step 19": False, "Step 20": False, "Step 21": False, "Step 22": False,
                    "Step 23": False, "Step 24": False, "Step 25": False, "Step 26": False, "Step 27": False,
                    "Step 28": False, "Step 29": False, "Step 30": False, "Step 31": False, "Step 32": False,
                    "Step 33": False}

    # Data for test case
    begin_time = 0
    pool_handle = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test9"
    wallet_name = "test_wallet9"


def test_precondition():
    """
    Clean up pool and wallet if they are exist.
    """
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    Common.clean_up_pool_and_wallet_folder(MyVars.pool_name, MyVars.wallet_name)


async def add_nym(submitter_did, target_did, ver_key, alias, role, can_add):
    """
    Build a NYM request and submit it to ledger

    :param submitter_did:
    :param target_did:
    :param ver_key:
    :param alias:
    :param role:
    :param can_add: if the expected result is the NYM can be added, can_add True.
                    if the expected result is the NYM cannot be added, can_add = False.

    :return: (True, message) if can_add = True and NYM can be added.
                             if can_add = False and NYM cannot be added.
             (False, message) if can_add = True and NYM cannot be added.
                              if can_add = False and NYM can be added.
    """
    result = False
    e = None
    try:
        nym_request = await ledger.build_nym_request(submitter_did, target_did, ver_key, alias, role)
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, submitter_did, nym_request)
        if can_add:
            result = True
    except IndyError as E:
        if not can_add:
            if E.error_code == 304:
                result = True
        else:
            e = str(E)
            print(Colors.FAIL + e + Colors.ENDC)

    return result, e


async def get_nym(submitter_did, target_did):
    """
    Build and submit a GET NYM request.

    :param submitter_did:
    :param target_did:
    :return: (True, message) if can execute GET NYM request.
             (False, message) if cannot execute GET NYM request.
    """
    try:
        get_nym_request = await ledger.build_get_nym_request(submitter_did, target_did)
        message = await ledger.submit_request(MyVars.pool_handle, get_nym_request)
        return True, message
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return False, str(E)


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


async def test_09_remove_and_add_role():
    """
    This function is the main part of test script.
    There is a bug in this scenario (in step 22, 23 24) so we log a bug here.
    """
    # 1. Create ledger config from genesis txn file.
    step = "Step01. Create pool ledger"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
        MyVars.test_results["Step 1"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 2. Open pool ledger.
    step = "Step02. Open pool ledger"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Step 2"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 3. Create wallet.
    step = "Step03. Create and open wallet"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # Get wallet handle.
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    MyVars.test_results["Step 3"] = True
    MyVars.test_report.set_step_status(step, Status.PASSED)

    # 4. Create DIDs.
    step = "Step04. Create DIDs"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    try:
        (default_trustee_did,
         default_trustee_verkey) = \
            await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                 json.dumps({"seed": Constant.seed_default_trustee}))

        (trustee1_did,
         trustee1_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustee2_did,
         trustee2_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward1_did,
         steward1_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward2_did,
         steward2_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward3_did,
         steward3_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (tgb1_did,
         tgb1_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor1_did,
         trustanchor1_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor2_did,
         trustanchor2_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor3_did,
         trustanchor3_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user1_did,
         user1_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user2_did,
         user2_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user3_did,
         user3_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user4_did,
         user4_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user5_did,
         user5_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (user6_did,
         user6_verkey) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))
        MyVars.test_results["Step 4"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 5. Using default Trustee to create Trustee1.
    step = "Step05. Using default Trustee to create Trustee1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 5"], message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                             None, Roles.TRUSTEE, can_add=True)
    if MyVars.test_results["Step 5"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 6. Verify GET NYM - Trustee1.
    step = "Step06. Verify GET NYM - Trustee1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 6"], message) = await get_nym(default_trustee_did, trustee1_did)

    if MyVars.test_results["Step 6"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 7. Using Trustee1 to create Steward1.
    step = "Step07. Using Trustee1 to create Steward1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 7"], message) = await add_nym(trustee1_did, steward1_did, steward1_verkey,
                                                             None, Roles.STEWARD, can_add=True)

    if MyVars.test_results["Step 7"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 8. Verify GET NYM - Steward1.
    step = "Step08. Verify GET NYM - Steward1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 8"], message) = await get_nym(trustee1_did, steward1_did)

    if MyVars.test_results["Step 8"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 9. Add identity (no role) by Trustee1.
    step = "Step09. Add identity (no role) by Trustee1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 9"], message) = await add_nym(trustee1_did, user3_did, user3_verkey,
                                                             None, None, can_add=True)

    if MyVars.test_results["Step 9"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 10. Verify GET NYM - no role.
    step = "Step10. Verify GET NYM - no role"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 10"], message) = await get_nym(trustee1_did, user3_did)

    if MyVars.test_results["Step 10"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # Role TGB is not exist so we do not execute step 11.
    # 11. Using Trustee1 to create a TGB role.
    # print(Colors.HEADER + "\n\t11.  Using Trustee1 to create a TGB role\n" + Colors.ENDC)
    # (MyVars.test_results["Step 11"], message) = await add_nym(trustee1_did, tgb1_did, tgb1_verkey,
    #                                                           None, Roles.TGB, can_add=True)
    #
    # if MyVars.test_results["Step 11"] is False:
    #     MyVars.test_report.set_test_failed()
    #     MyVars.test_report.set_step_status("Step11. Using Trustee1 to create a TGB role", str(message))

    MyVars.test_report.set_step_status("Step11. Using Trustee1 to create a TGB role (SKIP)")

    # Role TGB is not exist so we do not execute step 12.
    # 12. Verify GET NYM.
    # print(Colors.HEADER + "\n\t12.  Verify GET NYM - TGB1\n" + Colors.ENDC)
    # (MyVars.test_results["Step 12"], message) = await get_nym(trustee1_did, tgb1_did)
    #
    # if MyVars.test_results["Step 12"] is False:
    #     MyVars.test_report.set_test_failed()
    #     MyVars.test_report.set_step_status("Step12. Verify GET NYM - TGB1", str(message))
    MyVars.test_report.set_step_status("Step12. Verify GET NYM - TGB1 (SKIP)")

    # 13. Using Steward1 to create TrustAnchor1.
    step = "Step13. Using Steward1 to create TrustAnchor1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 13"], message) = await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                                              None, Roles.TRUST_ANCHOR, can_add=True)

    if MyVars.test_results["Step 13"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 14. Verify GET NYM.
    step = "Step14. Verify GET NYM - TrustAnchor1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 14"], message) = await get_nym(steward1_did, trustanchor1_did)

    if MyVars.test_results["Step 14"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 15. Verify add identity (no role) by Steward1.
    step = "Step15. Add identity (no role) by Steward1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 15"], message) = await add_nym(steward1_did, user4_did, user4_verkey,
                                                              None, None, can_add=True)

    if MyVars.test_results["Step 15"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 16. Verify GET NYM.
    step = "Step16. Verify GET NYM - no role"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 16"], message) = await get_nym(steward1_did, user4_did)

    if MyVars.test_results["Step 16"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 17. Verify that a Steward cannot create another Steward.
    step = "Step17. Verify that Steward cannot create another Steward"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=False)

    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Steward!\n" + Colors.ENDC)
        MyVars.test_results["Step 17"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create another Steward (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))

    # 18. Verify that a Steward cannot create a Trustee.
    step = "Step18. Verify that Steward cannot create a Trustee"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, Roles.TRUSTEE, can_add=False)

    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Step 18"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create a Trustee (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))

    # 19. Using TrustAnchor1 to add a NYM.
    step = "Step19. Using TrustAnchor1 to add a NYM"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 19"], message) = await add_nym(trustanchor1_did, user1_did, user1_verkey,
                                                              None, None, can_add=True)

    if MyVars.test_results["Step 19"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 20. Verify GET NYM.
    step = "Step20. Verify that new NYM added with TrustAnchor1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 20"], message) = await get_nym(trustanchor1_did, user1_did)

    if MyVars.test_results["Step 20"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 21. Verify that TrustAnchor cannot create another TrustAnchor.
    step = "Step21. Verify that TrustAnchor cannot create another TrustAnchor"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(trustanchor1_did, trustanchor2_did, trustanchor2_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        MyVars.test_results["Step 21"] = True
        print(Colors.OKGREEN + "::PASS::Validated that a TrustAnchor cannot create another TrustAnchor!\n"
              + Colors.ENDC)
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "TrustAnchor can create another TrustAnchor (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, str(message))

    # 22. Using default Trustee to remove new roles.
    bug_is_430 = "Bug: https://jira.hyperledger.org/browse/IS-430"
    step = "Step22. Using default Trustee to remove new roles"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    message_22 = ""
    (temp, message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                    None, "", can_add=True)
    MyVars.test_results["Step 22"] = temp
    if not temp:
        message_22 += "\nCannot remove Trustee1's role - " + message
    else:
        (temp, message) = await get_nym(default_trustee_did, trustee1_did)
        if not temp:
            message_22 += "\nCannot check GET_NYM for Trustee1 - " + message
        else:
            if not check_role_in_retrieved_nym(message, Roles.NONE):
                temp = False
                message_22 += "\nCannot remove Trustee1's role"

    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    (temp, message) = await add_nym(default_trustee_did, steward1_did, steward1_verkey,
                                    None, Roles.NONE, can_add=True)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot remove Steward1's role - " + message
    else:
        (temp, message) = await get_nym(default_trustee_did, steward1_did)
        if not temp:
            message_22 += "\nCannot check GET_NYM for Steward1 - " + message
        else:
            if not check_role_in_retrieved_nym(message, Roles.NONE):
                temp = False
                message_22 += "\nCannot remove Steward1's role"

    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp

    # Any step that involve to role TGB is skipped because role TGB is not supported by libindy
    # (temp, message) = await add_nym(default_trustee_did, tgb1_did, tgb1_verkey, None, Roles.NONE, can_add=True)
    # MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    # if not temp:
    #     message_22 += "\nCannot remove TGB's role - " + message
    # else:
    #     (temp, message) = await get_nym(default_trustee_did, tgb1_did)
    #     if not temp:
    #         message_22 += "\nCannot check GET_NYM for TGB - " + message
    #     else:
    #         if not check_role_in_retrieved_nym(message, Roles.NONE):
    #             temp = False
    #             message_22 += "\nCannot remove TGB1's role"
    #
    # MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp

    (temp, message) = await add_nym(default_trustee_did, trustanchor1_did, trustanchor1_verkey,
                                    None, Roles.NONE, can_add=True)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp

    if not temp:
        message_22 += "\nCannot remove Trust_Anchor1's role - " + message
    else:
        (temp, message) = await get_nym(default_trustee_did, trustanchor1_did)
        if not temp:
            message_22 += "\nCannot check GET_NYM for Trust_Anchor1 - " + message
        else:
            if not check_role_in_retrieved_nym(message, Roles.NONE):
                temp = False
                message_22 += "\nCannot remove Trust_Anchor1's role"

    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp

    if MyVars.test_results["Step 22"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, "{}\n{}".format(message_22[1:], bug_is_430))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 23. Verify that removed Trustee1 cannot create Trustee or Steward.
    step = "Step23. Verify that removed Trustee1 cannot create Trustee or Steward"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    message_23 = ""
    (temp, message) = await add_nym(trustee1_did, trustee2_did, trustee2_verkey, None, Roles.TRUSTEE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create another Trustee!\n" + Colors.ENDC)
    else:
        if message is None:
            message = ""
        message_23 += "\nRemoved Trustee can create Trustee (should fail) " + message

    MyVars.test_results["Step 23"] = temp

    (temp, message) = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create a Steward!\n" + Colors.ENDC)
    else:
        if message is None:
            message = ""
        message_23 += "\nRemoved Trustee can create Steward(should fail) " + message

    MyVars.test_results["Step 23"] = MyVars.test_results["Step 23"] and temp

    if MyVars.test_results["Step 23"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, "{}\n{}".format(message_23[1:], bug_is_430))
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 24. Verify that removed Steward1 cannot create TrustAnchor.
    step = "Step24. Verify that removed Steward1 cannot create TrustAnchor"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustanchor2_did, trustanchor2_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Steward1 cannot create a TrustAnchor!\n" + Colors.ENDC)
        MyVars.test_results["Step 24"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward1 can create a TrustAnchor (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, "{}\n{}".format(message, bug_is_430))

    # 25. Using default Trustee to create Trustee1.
    step = "Step25. Using default Trustee to create Trustee1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 25"], message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                              None, Roles.TRUSTEE, can_add=True)
    if MyVars.test_results["Step 25"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message)
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 26. Using Trustee1 to add Steward1 and TGB1.
    step = "Step26. Using Trustee1 to add Steward1"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    message_26 = ""
    (temp, message) = await add_nym(trustee1_did, steward1_did, steward1_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 26"] = temp
    if not temp:
        message_26 += "\nCannot use Trustee1 to add Steward1 - " + message

    # Role TGB is not exist so we do not execute this step
    # (temp, message) = await add_nym(trustee1_did, tgb1_did, tgb1_verkey, None, Roles.TGB, can_add=True)
    # MyVars.test_results["Step 26"] = MyVars.test_results["Step 26"] and temp
    # if not temp:
    #     message_26 += "\nCannot use Trustee1 to add TGB1 - " + message

    if MyVars.test_results["Step 26"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message_26[1:])
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee.
    step = "Step27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward1 cannot add back a TrustAnchor removed by TrustTee!\n"
              + Colors.ENDC)
        MyVars.test_results["Step 27"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward1 can add back TrustAnchor removed by Trustee (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, message)

    # 28. Verify that Steward cannot remove a Trustee.
    step = "Step28. Verify that Steward cannot remove a Trustee"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, Roles.NONE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Step 28"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create a Trustee (should fail)"
        MyVars.test_report.set_step_status(step, Status.FAILED, message)

    # 29. Verify that Trustee can add new Steward.
    step = "Step29. Verify that Trustee can add new Steward"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    message_29 = ""
    (temp, message) = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 29"] = temp
    if not temp:
        message_29 += "\nTrustee cannot add Steward1 (should pass) - " + message

    temp = await add_nym(trustee1_did, steward3_did, steward3_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 29"] = MyVars.test_results["Step 29"] and temp
    if not temp:
        message_29 += "\nTrustee cannot add Steward2 (should pass) - " + message

    if MyVars.test_results["Step 29"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message_29[1:])
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # 30. Verify that Steward cannot remove another Steward.
    step = "30. Verify that Steward cannot remove another Steward"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, steward2_did, steward2_verkey, None, Roles.NONE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove another Steward!\n" + Colors.ENDC)
        MyVars.test_results["Step 30"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        if message is None:
            message = "Steward can remove another Steward (should fail)"
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message)

    # 31. Verify Steward can add a TrustAnchor.
    step = "Step31. Verify Steward can add a TrustAnchor"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    (MyVars.test_results["Step 31"], message) = await add_nym(steward2_did, trustanchor3_did, trustanchor3_verkey,
                                                              None, Roles.TRUST_ANCHOR, can_add=True)

    if MyVars.test_results["Step 31"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message)
    else:
        MyVars.test_report.set_step_status(step, Status.PASSED)

    # =========================================================================================
    # Clean up here
    # =========================================================================================

    print(Colors.HEADER + "\n\t==Cleanup==" + Colors.ENDC)
    # 32. Close pool ledger and wallet.
    step = "Step32. Close pool ledger and wallet"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step 32"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 33. Delete pool ledger and wallet.
    step = "Step33. Delete pool ledger and wallet"
    print(Colors.HEADER + "\n\t{}\n".format(step) + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
        MyVars.test_results["Step 33"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)


def final_result():
    print("\nTest result================================================" + Colors.ENDC)
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)
    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()

    # Generate html single report:
    folder = MyVars.test_report.get_result_folder()

    if folder.find(MyVars.test_name) != -1:
        HTMLReport().make_html_report(folder, MyVars.test_name)


def test(folder_path=""):
    # Set up the report

    MyVars.begin_time = time.time()
    MyVars.test_report.change_result_dir(folder_path)
    MyVars.test_report.setup_json_report()

    test_precondition()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_09_remove_and_add_role())
    loop.close()

    final_result()


if __name__ == '__main__':
    test()
