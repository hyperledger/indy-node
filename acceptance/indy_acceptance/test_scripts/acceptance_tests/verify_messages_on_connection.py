"""
Created on Nov 8, 2017

@author: khoi.ngo

Containing test script of test scenario 02: verify messages on connection.
"""

import json
import os

from indy import pool

from indy_acceptance.utilities.constant import original_pool_genesis_txn_file,\
                               pool_genesis_txn_file
from indy_acceptance.utilities.result import Status
from indy_acceptance.utilities.utils import perform
from indy_acceptance.test_scripts.test_scenario_base import TestScenarioBase


""" cmds """
back_up_pool_genesis_file = 'sudo cp ' + pool_genesis_txn_file + \
    " " + original_pool_genesis_txn_file
remove_pool_genesis_file = 'sudo rm ' + pool_genesis_txn_file
restore_pool_genesis_file = 'sudo cp ' + \
    original_pool_genesis_txn_file + " " + pool_genesis_txn_file
create_empty_pool_genesis_file = 'sudo touch ' + pool_genesis_txn_file


class VerifyMessagesOnConnection(TestScenarioBase):

    async def execute_precondition_steps(self):
        os.system(back_up_pool_genesis_file)
        os.system(remove_pool_genesis_file)
        os.system(create_empty_pool_genesis_file)

    async def execute_postcondition_steps(self):
        os.system(remove_pool_genesis_file)
        os.system(restore_pool_genesis_file)

    async def execute_test_steps(self):
        # 1. Create ledger config from genesis txn file
        self.steps.add_step("Create Ledger")
        pool_config = json.dumps(
            {"genesis_txn": str(self.pool_genesis_txn_file)})
        self.pool_handle = await perform(self.steps,
                                         pool.create_pool_ledger_config,
                                         self.pool_name, pool_config,
                                         ignore_exception=False)

        # 2. Open pool ledger -------------------------------------------------
        self.steps.add_step("Open pool ledger")
        bug_is332 = "Bug: https://jira.hyperledger.org/browse/IS-332"
        message_2 = "Failed due to the Bug IS-332" + "\n" + bug_is332
        self.steps.get_last_step().set_status(Status.FAILED, message_2)

        # 3. verifying the message --------------------------------------------
        self.steps.add_step("verifying the message")
        message_3 = "TODO after fix IS-332"
        self.steps.get_last_step().set_status(Status.FAILED, message_3)


if __name__ == '__main__':
    VerifyMessagesOnConnection().execute_scenario()
