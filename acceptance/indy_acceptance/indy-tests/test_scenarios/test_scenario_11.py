'''
Created on Nov 8, 2017

@author: khoi.ngo
'''
# /usr/bin/env python3.6
import sys
import asyncio
import json
import logging
import time
import os
from indy import ledger, signus, wallet, pool
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import generate_random_string
from utils.constant import Colors, Constant, Roles
from utils.report import TestReport, Status, HTMLReport
from utils.common import Common
# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    wallet_handle = 0
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    test_name = "Test_Scenario_11_Special_Case_Trust_Anchor_Role"
    test_report = TestReport(test_name)
    test_results = {"Step1": False, "Step2": False, "Step3": False, "Step4": False,
                    "Step5": False, "Step6": False, "Step7": False, "Step8": False,
                    "Step9": False, "Step10": False, "Step11": False, "Step12": False,
                    "Step13": False, "Step14": False, "Step15": False, "Step16": False,
                    "Step17": False, "Step18": False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    """  Delete all files out of the .sovrin/pool and .sovrin/wallet directories  """
    print(Colors.HEADER + "\nPrecondition \n" + Colors.ENDC)
    Common.clean_up_pool_and_wallet_folder(MyVars.pool_name, MyVars.wallet_name)


async def test_scenario_11_special_case_trust_anchor_role():
    logger.info("Test Scenario 11 -> started")

    # Declare all values use in the test
    seed_trustee1 = generate_random_string(prefix="Trustee1", size=32)
    seed_trustee2 = generate_random_string(prefix="Trustee2", size=32)
    seed_steward1 = generate_random_string(prefix="Steward1", size=32)
    seed_steward2 = generate_random_string(prefix="Steward2", size=32)
    seed_trustanchor1 = generate_random_string(prefix="TrustAnchor1", size=32)
    seed_trustanchor2 = generate_random_string(prefix="TrustAnchor2", size=32)
    seed_trustanchor3 = generate_random_string(prefix="TrustAnchor3", size=32)

    # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
    step = "Step01. Create and open pool Ledger"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        MyVars.pool_handle, MyVars.wallet_handle = await Common.prepare_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name, MyVars.pool_genesis_txn_file)
        MyVars.test_results["Step1"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return
    await asyncio.sleep(0)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nWallet handle is %s" % str(MyVars.wallet_handle) + Colors.ENDC)

    # 2. Create DIDs ----------------------------------------------------
    step = "Step02. Create DIDs"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        (default_trustee_did, default_trustee_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": Constant.seed_default_trustee}))

        (trustee1_did, trustee1_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trustee1}))
        (trustee2_did, trustee2_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trustee2}))
        (steward1_did, steward1_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_steward1}))
        (steward2_did, steward2_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_steward2}))
        (trustanchor1_did, trustanchor1_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trustanchor1}))
        (trustanchor2_did, trustanchor2_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trustanchor2}))
        (trustanchor3_did, trustanchor3_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trustanchor3}))
        MyVars.test_results["Step2"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDID's created..." + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================

    # 3. Using the default Trustee create a TrustAnchor and a new Trustee----------------------------------------------
    # Create a dict for the parts of this test, use this to determine if everything worked
    step = "Step03. Use default Trustee to create a Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req5 = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, Roles.TRUSTEE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req5)
        MyVars.test_results["Step3"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 4. Verify GET_NYM for trustee1-----------------------------------------------------------------------------------
    step = "Step04. Verify get nym for Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    get_nym_txn_req5a = await ledger.build_get_nym_request(default_trustee_did, trustee1_did)
    try:
        await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req5a)
        MyVars.test_results["Step4"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5. TrustAnchor1
    step = "Step05. Verify get nym for Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req5b = await ledger.build_nym_request(default_trustee_did, trustanchor1_did, trustanchor1_verkey, None,
                                                   Roles.TRUST_ANCHOR)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req5b)
        MyVars.test_results["Step5"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 6. Verify GET_NYM for TrustAnchor1-------------------------------------------------------------------------------
    step = "Step06. Verify get nym for Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    get_nym_txn_req5c = await ledger.build_get_nym_request(default_trustee_did, trustanchor1_did)
    try:
        await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req5c)
        MyVars.test_results["Step6"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 7. Using the TrustAnchor create a Trustee (Trust Anchor should not be able to create Trustee) --------------------
    step = "Step07. Use TrustAnchor1 to create a Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)

    nym_txn_req6 = await ledger.build_nym_request(trustanchor1_did, trustee2_did, trustee2_verkey, None, Roles.TRUSTEE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req6)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results["Step7"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    # 8. Verify GET_NYM for new Trustee--------------------------------------------------------------------------------
    step = "Step08. Verify get NYM for new trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    get_nym_txn_req6a = await ledger.build_get_nym_request(trustanchor1_did, trustee2_did)
    try:
        await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req6a)
        MyVars.test_results["Step8"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 9. Verify that the TestTrustAnchorTrustee cannot create a new Steward
    step = "Step09. Verify a trustee cannot create a new Steward"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req7 = await ledger.build_nym_request(trustee2_did, steward1_did, steward1_verkey, None, Roles.STEWARD)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee2_did, nym_txn_req7)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results["Step9"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTestTrustAnchorTrustee cannot create a steward" + Colors.ENDC)

    await asyncio.sleep(0)

    # 10. Using the TrustAnchor blacklist a Trustee (TrustAnchor should not be able to blacklist Trustee)
    step = "Step10. Use TrustAnchor to blacklist a Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req8 = await ledger.build_nym_request(trustanchor1_did, trustee1_did, trustee1_verkey, None, Roles.NONE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req8)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results["Step10"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 11. Verify Trustee was not blacklisted by creating another Trustee------------------------------------------------
    step = "Step11. Verify Trustee was not blacklisted by creating another Trustee"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    get_nym_txn_req8a = await ledger.build_nym_request(trustee1_did, trustee2_did, trustee2_verkey, None, Roles.TRUSTEE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, get_nym_txn_req8a)
        MyVars.test_results["Step11"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 12. Using the TrustAnchor1 to create a Steward2 -----------------------------------------------------------------
    step = "Step12. Use TrustAnchor1 to create a Steward2"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req9 = await ledger.build_nym_request(trustanchor1_did, steward2_did, steward2_verkey, None, Roles.STEWARD)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req9)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results["Step12"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 13. Using the TrustAnchor1 blacklist Steward1 -----------------------------------------------------------------
    step = "Step13. Add Steward1 for the test"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    setup_10 = await ledger.build_nym_request(trustee1_did, steward1_did, steward1_verkey, None, Roles.STEWARD)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, setup_10)
        MyVars.test_results["Step13"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 14. Now run the test to blacklist Steward1
    step = "Step14. Run the test to blacklist Steward1"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req10 = await ledger.build_nym_request(trustanchor1_did, steward1_did, steward1_verkey, None, Roles.NONE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req10)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results["Step14"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 15. Verify that a TrustAnchor1 cannot create another TrustAnchor3 -------------------------------------
    step = "Step15. Verify TrustAnchor1 cannot create a TrustAnchor3"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req11 = await ledger.build_nym_request(trustanchor1_did, trustanchor3_did, trustanchor3_verkey, None,
                                                   Roles.TRUST_ANCHOR)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req11)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results["Step15"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    # 16. Verify that a TrustAnchor1 cannot blacklist another TrustAnchor2 -------------------------------------
    step = "Step16. Verify TrustAnchor1 cannot blacklist TrustAnchor2"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    nym_txn_req11 = await ledger.build_nym_request(trustanchor1_did, trustanchor2_did, trustanchor2_verkey, None,
                                                   Roles.NONE)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor2_did,
                                             nym_txn_req11)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results["Step16"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        else:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTrustAnchor cannot blacklist another TrustAnchor" + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 17. Close wallet and pool ------------------------------------------------------------------------------
    step = "Step17. Close and delete the wallet and the pool ledger..."
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step17"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nClosed wallet and pool\n" + Colors.ENDC)

    # 18. Delete wallet and pool ledger --------------------------------------------------------------------
    step = "Step18. Delete the wallet and pool ledger..."
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
        MyVars.test_results["Step18"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nDeleted wallet and pool ledger\n" + Colors.ENDC)

    logger.info("Test Scenario 11 -> completed")


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
    loop.run_until_complete(test_scenario_11_special_case_trust_anchor_role())
    loop.close()

    final_result()


if __name__ == '__main__':
    test()
