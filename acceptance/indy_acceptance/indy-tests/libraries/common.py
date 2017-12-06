"""
Created on Nov 13, 2017

@author: khoi.ngo

Containing all functions that is common among test scenarios.
"""

import asyncio
import json
from indy import wallet, pool, ledger
from .constant import Colors, Constant, Message


class Common:
    """
    Wrapper common function for test scenario.
    """

    @staticmethod
    async def prepare_pool_and_wallet(pool_name, wallet_name, pool_genesis_txn_file):
        """
        Prepare pool and wallet to use in a test case.

        :param pool_name: Name of the pool ledger configuration.
        :param wallet_name: Name of the wallet.
        :param pool_genesis_txn_file: The path of the pool_genesis_transaction file.
        :return: The pool handle and the wallet handle were created.
        """
        pool_handle = await Common().create_and_open_pool(pool_name, pool_genesis_txn_file)
        wallet_handle = await Common().create_and_open_wallet(pool_name, wallet_name)
        return pool_handle, wallet_handle

    @staticmethod
    async def clean_up_pool_and_wallet(pool_name, pool_handle, wallet_name, wallet_handle):
        """
        Clean up pool and wallet. Using as a post condition of a test case.

        :param pool_name: The name of the pool.
        :param pool_handle: The handle of the pool.
        :param wallet_name: The name of the wallet.
        :param wallet_handle: The handle of the wallet.
        """
        await Common().close_pool_and_wallet(pool_handle, wallet_handle)
        await Common().delete_pool_and_wallet(pool_name, wallet_name)

    @staticmethod
    def clean_up_pool_and_wallet_folder(pool_name, wallet_name):
        """
        Delete pool and wallet folder without using lib-indy.

        :param pool_name: The name of the pool.
        :param wallet_name: The name of the wallet.
        """
        import os
        import shutil
        work_dir = Constant.work_dir

        if os.path.exists(work_dir + "/pool/" + pool_name):
            try:
                shutil.rmtree(work_dir + "/pool/" + pool_name)
            except IOError as E:
                print(Colors.FAIL + str(E) + Colors.ENDC)

        if os.path.exists(work_dir + "/wallet/" + wallet_name):
            try:
                shutil.rmtree(work_dir + "/wallet/" + wallet_name)
            except IOError as E:
                print(Colors.FAIL + str(E) + Colors.ENDC)

    @staticmethod
    async def build_and_send_nym_request(pool_handle, wallet_handle, submitter_did,
                                         target_did, target_verkey, alias, role):
        """
        Build a nym request and send it.

        :param pool_handle: pool handle returned by indy_open_pool_ledger.
        :param wallet_handle: wallet handle returned by indy_open_wallet.
        :param submitter_did: Id of Identity stored in secured Wallet.
        :param target_did: Id of Identity stored in secured Wallet.
        :param target_verkey: verification key.
        :param alias: alias.
        :param role: Role of a user NYM record.
        :raise Exception if the method has error.
        """
        nym_txn_req = await ledger.build_nym_request(submitter_did, target_did, target_verkey, alias, role)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, nym_txn_req)

    @staticmethod
    async def create_and_open_pool(pool_name, pool_genesis_txn_file):
        """
        Creates a new local pool ledger configuration.
        Then open that pool and return the pool handle that can be used later to connect pool nodes.

        :param pool_name: Name of the pool ledger configuration.
        :param pool_genesis_txn_file: Pool configuration json. if NULL, then default config will be used.
        :return: The pool handle was created.
        """
        import os
        if os.path.exists(pool_genesis_txn_file) is not True:
            error_message = Colors.FAIL + "\n{}\n".format(Message.ERR_PATH_DOES_NOT_EXIST.format(Constant.pool_genesis_txn_file)) + Colors.ENDC
            raise ValueError(error_message)

        print(Colors.HEADER + "\nCreate Ledger\n" + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_file)})
        await pool.create_pool_ledger_config(pool_name, pool_config)

        print(Colors.HEADER + "\nOpen pool ledger\n" + Colors.ENDC)
        pool_handle = await pool.open_pool_ledger(pool_name, None)
        return pool_handle

    @staticmethod
    async def create_and_open_wallet(pool_name, wallet_name):
        """
        Creates a new secure wallet with the given unique name.
        Then open that wallet and get the wallet handle that can
        be used later to use in methods that require wallet access.

        :param pool_name: Name of the pool that corresponds to this wallet.
        :param wallet_name: Name of the wallet.
        :return: The wallet handle was created.
        """
        print(Colors.HEADER + "\nCreate wallet\n" + Colors.ENDC)
        await wallet.create_wallet(pool_name, wallet_name, None, None, None)

        print(Colors.HEADER + "\nGet wallet handle\n" + Colors.ENDC)
        wallet_handle = await wallet.open_wallet(wallet_name, None, None)
        return wallet_handle

    @staticmethod
    async def close_pool_and_wallet(pool_handle, wallet_handle):
        """
        Close the pool and wallet with the pool and wallet handle.

        :param pool_handle: pool handle returned by indy_open_pool_ledger.
        :param wallet_handle: wallet handle returned by indy_open_wallet.
        :raise Exception if the method has error.
        """
        print(Colors.HEADER + "\nClose pool\n" + Colors.ENDC)
        await pool.close_pool_ledger(pool_handle)

        print(Colors.HEADER + "\nClose wallet\n" + Colors.ENDC)
        await wallet.close_wallet(wallet_handle)

    @staticmethod
    async def delete_pool_and_wallet(pool_name, wallet_name):
        """
        Delete the pool and wallet with the pool and wallet name.

        :param pool_name: Name of the pool that corresponds to this wallet.
        :param wallet_name: Name of the wallet to delete.
        :raise Exception if the method has error.
        """
        print(Colors.HEADER + "\nDelete pool\n" + Colors.ENDC)
        await pool.delete_pool_ledger_config(pool_name)

        print(Colors.HEADER + "\nDelete wallet\n" + Colors.ENDC)
        await wallet.delete_wallet(wallet_name, None)
        await asyncio.sleep(0)
