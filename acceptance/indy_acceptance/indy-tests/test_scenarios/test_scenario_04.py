'''
Created on Nov 8, 2017

@author: khoi.ngo
'''
# /usr/bin/env python3.6
import sys
import asyncio
import json
import os.path
import logging
import time
from indy import signus
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import generate_random_string
from utils.constant import Colors, Constant
from utils.common import Common
from utils.report import TestReport, Status, HTMLReport

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class MyVars:
    """  Needed some global variables. """
    begin_time = 0
    pool_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    wallet_handle = 0
    test_name = "Test_scenario_04_Keyrings_Wallets"
    test_report = TestReport(test_name)
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    test_results = {'Step1': False, 'Step2': False, 'Step3': False, 'Step4': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
    print(Colors.HEADER + "\nPrecondition \n" + Colors.ENDC)
    Common.clean_up_pool_and_wallet_folder(MyVars.pool_name, MyVars.wallet_name)


async def test_scenario_04_keyrings_wallets():
    logger.info("Test Scenario 04 -> started")
    seed_default_trustee = "000000000000000000000000Trustee1"

    # 1. Create and open pool Ledger  ---------------------------------------------------------
    step = "Step01. Create and open pool Ledger"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        MyVars.pool_handle, MyVars.wallet_handle = await Common.prepare_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name, MyVars.pool_genesis_txn_file)
        MyVars.test_results['Step1'] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 2. verify wallet was created in .indy/wallet
    step = "Step02. Verify wallet was created in .indy/wallet"
    try:
        print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
        work_dir = os.path.expanduser('~') + os.sep + ".indy"
        wallet_path = work_dir + "/wallet/" + MyVars.wallet_name
        result = os.path.exists(wallet_path)
        if result:
            MyVars.test_results['Step2'] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
            print("===PASSED===")
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 3. create DID to check the new wallet work well.
    step = "Step03. Create DID to check the new wallet work well"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        # create and store did to check the new wallet work well.
        (default_trustee_did, default_trustee_verkey) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))
        if default_trustee_did:
            MyVars.test_results['Step3'] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
            print("===PASSED===")
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 4. Close wallet and pool ------------------------------------------------------------------------------
    step = "Step04. Close and delete the wallet and the pool ledger..."
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await Common.clean_up_pool_and_wallet(MyVars.pool_name, MyVars.pool_handle, MyVars.wallet_name, MyVars.wallet_handle)
        MyVars.test_results['Step4'] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
        print("===PASSED===")
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    logger.info("Test Scenario 04 -> completed")


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
    loop.run_until_complete(test_scenario_04_keyrings_wallets())
    loop.close()

    final_result()


if __name__ == '__main__':
    test()
