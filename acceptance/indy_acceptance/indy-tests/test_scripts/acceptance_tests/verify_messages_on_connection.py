"""
Created on Nov 8, 2017

@author: khoi.ngo

Containing test script of test scenario 02: verify messages on connection.
"""

import json
import os
from indy import pool
from libraries.constant import Constant, Colors
from libraries.result import Status
from libraries.utils import perform
from test_scripts.test_scenario_base import TestScenarioBase

""" cmds """
back_up_pool_genesis_file = 'sudo cp ' + Constant.pool_genesis_txn_file + " " + Constant.original_pool_genesis_txn_file
remove_pool_genesis_file = 'sudo rm ' + Constant.pool_genesis_txn_file
restore_pool_genesis_file = 'sudo cp ' + Constant.original_pool_genesis_txn_file + " " + Constant.pool_genesis_txn_file
create_empty_pool_genesis_file = 'sudo touch ' + Constant.pool_genesis_txn_file


class TestScenario02(TestScenarioBase):

    async def execute_precondition_steps(self):
        os.system(back_up_pool_genesis_file)
        os.system(remove_pool_genesis_file)
        os.system(create_empty_pool_genesis_file)

    async def execute_postcondition_steps(self):
        os.system(remove_pool_genesis_file)
        os.system(restore_pool_genesis_file)

    async def execute_test_steps(self):
        print("Test Scenario 02 -> started")
        try:
            # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
            self.steps.add_step("Create Ledger")
            pool_config = json.dumps({"genesis_txn": str(self.pool_genesis_txn_file)})
            self.pool_handle = await perform(self.steps, pool.create_pool_ledger_config, self.pool_name, pool_config)

            # 2. Open pool ledger -----------------------------------------------------------------------------------
            self.steps.add_step("Open pool ledger")
            self.steps.get_last_step().set_message("Failed due to the Bug IS-332")
            self.steps.get_last_step().set_status(Status.FAILED)

            # 3. verifying the message ------------------------------------------------------------------------
            self.steps.add_step("verifying the message")
            self.steps.get_last_step().set_message("TODO after fix IS-332")
            self.steps.get_last_step().set_status(Status.FAILED)
        except Exception as ex:
            print(Colors.FAIL + "Exception: " + str(ex) + Colors.ENDC)

        print("Test Scenario 02 -> completed")


if __name__ == '__main__':
    TestScenario02().execute_scenario()
