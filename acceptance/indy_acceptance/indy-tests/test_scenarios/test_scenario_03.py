import json
import sys
import logging
import os
import asyncio
import shutil
import time
from indy import pool, signus, wallet
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Colors, Constant
from utils.report import TestReport, Status, HTMLReport
from utils.common import Common


class MyVars:
    # Data for generating report
    test_name = "Test_scenario_03_Check_Connection"
    test_report = TestReport(test_name)
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False,
                    "Step 5": False, "Step 6": False, "Step 7": False, "Step 8": False}

    # Data using in testcase
    begin_time = 0
    pool_handle = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test3"
    wallet_name = "test_wallet3"
    debug = False
    seed_steward01 = "000000000000000000000000Steward1"


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    # Precondition steps:
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    Common.clean_up_pool_and_wallet_folder(MyVars.pool_name, MyVars.wallet_name)


async def test_scenario_03_check_connection():
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})

    logger.info("{0} -> started".format(MyVars.test_name))

    # 1. Create pool ledger
    step = "Step01. Create pool ledger"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:

        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)

        MyVars.test_results["Step 1"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 2. Create wallet
    step = "Step02. Create wallet"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    temp = None
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
        temp = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        temp = False
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    MyVars.test_results["Step 2"] = temp

    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
        temp = True
        MyVars.test_report.set_step_status("Step02. Create wallet", Status.PASSED)
    except IndyError as E:
        temp = False
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step02. Create wallet", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
    MyVars.test_results["Step 2"] = MyVars.test_results["Step 2"] and temp

    # 3. Create DID
    step = "Step03. Create DID"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({"seed": MyVars.seed_steward01}))
        MyVars.test_results["Step 3"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 4. Connect to pool.
    # Verify that the default wallet move to Test from NoEnv?
    # Cannot verify because ".indy/wallet" do not include any folder that name
    # no-env and test, and default wallet cannot be created via indy-sdk
    step = "Step04. Connect to pool"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Step 4"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5. Disconnect from pool.
    step = "Step05. Disconnect form pool"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step 5"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 6. Reconnect to pool.
    step = "Step06. Reconnect to pool"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Step 6"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t==Clean up==" + Colors.ENDC)

    # 7. Close pool ledger and wallet.
    step = "Step07. Close pool ledger and wallet"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step 7"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 8. Delete wallet.
    step = "Step08. Delete pool ledger and wallet"
    print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
        MyVars.test_results["Step 8"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test scenario 3 -> finished")


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
    loop.run_until_complete(test_scenario_03_check_connection())
    loop.close()

    final_result()


if __name__ == '__main__':
    test()

