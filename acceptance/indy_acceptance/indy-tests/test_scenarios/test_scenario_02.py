import asyncio
import json
import logging
import os
import sys
import time
from indy import pool
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Constant, Colors
from utils.utils import generate_random_string
from utils.report import HTMLReport
from utils.report import TestReport, Status


# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class MyVars:
    # Data for generating report
    test_name = "Test_Scenario_02_Verify_Messages_On_Connection"
    test_report = TestReport(test_name)
    the_error_message = "the information needed to connect was not found"
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False}

    """  Needed some global variables. """
    pool_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    original_pool_genesis_txn_file = Constant.original_pool_genesis_txn_file
    pool_name = generate_random_string("test_pool", size=20)
    debug = False

    # cmds
    back_up_pool_genesis_file = 'cp ' + pool_genesis_txn_file + " " + original_pool_genesis_txn_file
    exit_sovrin = 'exit'
    remove_pool_genesis_file = 'rm ' + pool_genesis_txn_file
    restore_pool_genesis_file = 'cp ' + original_pool_genesis_txn_file + " " + pool_genesis_txn_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run(cmd):
    os.system(cmd)


def test_precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    print(Colors.HEADER + "\nPrecondition \n" + Colors.ENDC)
    run(MyVars.back_up_pool_genesis_file)
    open(MyVars.pool_genesis_txn_file, 'w').close()


async def test_scenario_02_verify_messages_on_connection():
    logger.info("Test Scenario 02 -> started")

    try:
        # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
        step = "Step1.  Create Ledger"
        print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})

        try:
            await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)

            MyVars.test_results["Step 1"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        except IndyError as E:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)
            return
        await asyncio.sleep(0)

        # 2. Open pool ledger -----------------------------------------------------------------------------------
        step = "Step2.  Open pool ledger"
        print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
        try:
            print(Colors.FAIL + "Failed due to the Bug IS-332" + Colors.ENDC)
            print(Colors.UNDERLINE + "https://jira.hyperledger.org/browse/IS-332" + Colors.ENDC)

            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, "Failed due to the Bug IS-332 https://jira.hyperledger.org/browse/IS-332")
            return
        except IndyError as E:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)
            return

        # 3. verifying the message ------------------------------------------------------------------------
        step = "Step3. verifying the message"
        print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)

        try:
            print("TODO after fix IS-332")
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]
    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    finally:
        # 4. Restore the pool_transactions_sandbox_genesis file-------------------------------------------------
        step = "Step4. Restore the pool_transactions_sandbox_genesis file"
        print(Colors.HEADER + "\n\t {0}\n".format(step) + Colors.ENDC)
        try:
            run(MyVars.remove_pool_genesis_file)
            run(MyVars.restore_pool_genesis_file)

            MyVars.test_results["Step 4"] = True
            MyVars.test_report.set_step_status(step, Status.PASSED)
        except IndyError as E:
            MyVars.test_report.set_test_failed()
            MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
            print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test Scenario 02 -> completed")


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
    MyVars.test_report.setup_json_report();

    test_precondition()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_scenario_02_verify_messages_on_connection())
    loop.close()

    final_result()

if __name__ == '__main__':
    test()

