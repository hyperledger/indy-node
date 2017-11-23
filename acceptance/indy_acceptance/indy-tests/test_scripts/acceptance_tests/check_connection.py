"""
Created on Nov 10, 2017

@author: nhan.nguyen

Containing test script of test scenario 03: check connection.
"""

import json
import sys
import os
from indy import pool, signus, wallet
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from libraries.constant import Constant, Colors
from libraries.utils import *
from test_scripts.test_scenario_base import TestScenarioBase


class TestScenario03(TestScenarioBase):
    seed_steward01 = "000000000000000000000000Steward1"

    async def execute_test_steps(self):
        try:
            pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})
            # 1. Create pool ledger
            self.steps.add_step("Create pool ledger")
            await perform(self.steps, pool.create_pool_ledger_config, self.pool_name, pool_config)

            # 2. Create wallet
            self.steps.add_step("Create wallet")
            await perform(self.steps, wallet.create_wallet, self.pool_name, self.wallet_name, None, None, None)
            self.wallet_handle = await perform(self.steps, wallet.open_wallet, self.wallet_name, None, None)

            # 3. Create DID
            self.steps.add_step("Create DID")
            await perform(self.steps, signus.create_and_store_my_did,
                          self.wallet_handle, json.dumps({"seed": self.seed_steward01}))

            # 4. Connect to pool.
            # Verify that the default wallet move to Test from NoEnv?
            # Cannot verify because ".indy/wallet" do not include any folder that name
            # no-env and test, and default wallet cannot be created via indy-sdk
            self.steps.add_step("Connect to pool")
            self.pool_handle = await perform(self.steps, pool.open_pool_ledger, self.pool_name, None)

            # 5. Disconnect from pool.
            self.steps.add_step("Disconnect form pool")
            await perform(self.steps, pool.close_pool_ledger, self.pool_handle)

            # 6. Reconnect to pool.
            self.steps.add_step("Reconnect to pool")
            self.pool_handle = await perform(self.steps, pool.open_pool_ledger, self.pool_name, None)
        except Exception as e:
            print(Colors.FAIL + "\n\t{}\n".format(str(e)) + Colors.ENDC)


if __name__ == '__main__':
    TestScenario03().execute_scenario()
