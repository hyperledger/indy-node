"""
Created on Feb 27, 2018

@author: nhan.nguyen

This module contains class "Tester" that is the base class of other
tester classes.
"""

import utils
import json

from indy import wallet, pool, signus
from indy.error import IndyError


class Tester:

    def __init__(self, log, seed):
        self.pool_name = utils.generate_random_string(prefix="pool")
        self.wallet_name = utils.generate_random_string(prefix='wallet')
        self.pool_handle = self.wallet_handle = 0
        self.log = log
        self.seed = seed
        self.config = utils.parse_config()

        self.threads = list()
        self.passed_req = self.failed_req = 0
        self.start_time = self.finish_time = 0
        self.fastest_txn = self.lowest_txn = -1

    async def test(self):
        """
        The function execute testing steps.
        """
        if not self.log:
            utils.start_capture_console()

        # 1. Create pool config.
        await self._create_pool_config()

        # 2. Open pool ledger
        await self._open_pool()

        # 3. Create My Wallet and Get Wallet Handle
        await self._create_wallet()
        await self._open_wallet()

        # 4 Create and sender DID
        await self._create_submitter_did()

        await self._test()

        await self._close_pool_and_wallet()
        utils.print_header("\n\t======== Finished ========")

        utils.stop_capture_console()

    def get_elapsed_time(self):
        """
        Return elapsed time of testing step.
        :return: elapsed time.
        """
        return self.finish_time - self.start_time

    async def _test(self):
        """
        The function that execute main steps for testing.
        All base class should override this method.
        """
        pass

    async def _create_pool_config(self):
        """
        Create pool configuration from genesis file.
        """
        try:
            utils.print_header("\n\n\tCreate ledger config "
                               "from genesis txn file")

            pool_config = json.dumps(
                {'genesis_txn': self.config.pool_genesis_file})
            await pool.create_pool_ledger_config(self.pool_name,
                                                 pool_config)
        except IndyError as e:
            if e.error_code == 306:
                utils.print_warning("The ledger already exists, moving on...")
            else:
                utils.print_error(str(e))
                raise

    async def _open_pool(self):
        """
        Open pool config and get wallet handle.
        """
        try:
            utils.print_header("\n\tOpen pool ledger")
            self.pool_handle = await pool.open_pool_ledger(
                self.pool_name,
                None)
        except IndyError as e:
            utils.print_error(str(e))

    async def _create_wallet(self):
        """
        Create wallet.
        """

        try:
            utils.print_header("\n\tCreate wallet")
            await wallet.create_wallet(self.pool_name,
                                       self.wallet_name,
                                       None, None, None)
        except IndyError as e:
            if e.error_code == 203:
                utils.print_warning(
                    "Wallet '%s' already exists.  "
                    "Skipping wallet creation..." % str(
                        self.wallet_name))
            else:
                utils.print_error(str(e))
                raise

    async def _open_wallet(self):
        """
        Open wallet and get wallet handle.
        """

        try:
            utils.print_header("\n\tOpen wallet")
            self.wallet_handle = await wallet.open_wallet(
                self.wallet_name,
                None, None)
        except IndyError as e:
            utils.print_error(str(e))
            raise

    async def _create_submitter_did(self):
        try:
            utils.print_header("\n\tCreate DID to use when sending")

            self.submitter_did, _ = await signus.create_and_store_my_did(
                self.wallet_handle, json.dumps({'seed': self.seed}))

        except Exception as e:
            utils.print_error(str(e))
            raise

    async def _close_pool_and_wallet(self):
        """
        Clean up after testing complete.
        """
        utils.print_header("\n\tClose wallet")
        try:
            await wallet.close_wallet(self.wallet_handle)
        except Exception as e:
            utils.print_error("Cannot close wallet."
                              "Skip closing wallet...")
            utils.print_error(str(e))

        utils.print_header("\n\tClose pool")
        try:
            await pool.close_pool_ledger(self.pool_handle)
        except Exception as e:
            utils.print_error("Cannot close pool."
                              "Skip closing pool...")
            utils.print_error(str(e))

        utils.print_header("\n\tDelete wallet")
        try:
            await wallet.delete_wallet(self.wallet_name, None)
        except Exception as e:
            utils.print_error("Cannot delete wallet."
                              "Skip deleting wallet...")
            utils.print_error(str(e))

        utils.print_header("\n\tDelete pool")
        try:
            await pool.delete_pool_ledger_config(self.pool_name)
        except Exception as e:
            utils.print_error("Cannot delete pool."
                              "Skip deleting pool...")
            utils.print_error(str(e))
