'''
Created on Feb 26, 2018

@author: khoi.ngo
'''
import argparse
from asyncio.events import get_event_loop
import json

from indy import ledger, signus, pool, wallet


class Options:
    """
    This class use to pass the value from command line.
    """
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='This script will show the current number of '
            'transaction and then show how many transactions per minute.')

        parser.add_argument('-c',
                            help='Use to get current seqNo of transactions',
                            action='store_true',
                            default=False, required=False, dest='count')

        parser.add_argument('-s',
                            help='It is the starting seqNo of the transaction',
                            action='store',
                            default=False, required=False, dest='start_seqNo')

        parser.add_argument('-e',
                            help='It is the ending seqNo of the transaction',
                            action='store',
                            default=False, required=False, dest='end_seqNo')
        self.args = parser.parse_args()


class Colors:
    """ Class to set the colors for text. """
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color.


class Var:
    pool_handle = 0
    wallet_handle = 0


def force_print_to_console(message: str, color: str):
    """
    Force print a message to console (no matter log is captured or not).

    :param message:
    :param color:
    """
    msg = color + message + Colors.ENDC
    print(msg)


def print_green(message: str):
    """
    Force print a message with green color to console
    (no matter log is captured or not).
    :param message:
    """
    force_print_to_console(message, Colors.OKGREEN)


def print_error(message: str):
    """
    Force print a message with green color to console
    (no matter log is captured or not).
    :param message:
    """
    force_print_to_console(message, Colors.FAIL)


def generate_random_string(prefix="", suffix="", size=20):
    """
    Generate random string .
    :param prefix:  (optional) Prefix of a string.
    :param suffix:  (optional) Suffix of a string.
    :param size: (optional) Max length of a string (include prefix and suffix)
    :return: The random string.
    """
    import random
    import string
    left_size = size - len(prefix) - len(suffix)
    random_str = ""
    if left_size > 0:
        random_str = ''.join(
            random.choice(string.ascii_uppercase +
                          string.digits) for _ in range(left_size))
    else:
        print("Warning: Length of prefix and suffix more than %s chars"
              % str(size))
    result = str(prefix) + random_str + str(suffix)
    return result


async def create_submitter_did():
    try:
        # variable
        pool_txn = "/var/lib/indy/sandbox/pool_transactions_genesis"
        pool_name = generate_random_string("test_pool")
        wallet_name = generate_random_string("test_wallet")
        seed_default_steward = "000000000000000000000000Steward1"
        pool_config = json.dumps({"genesis_txn": pool_txn})

        # Create pool
        await pool.create_pool_ledger_config(pool_name, pool_config)
        Var.pool_handle = await pool.open_pool_ledger(pool_name, None)

        # Create Wallet
        await wallet.create_wallet(pool_name, wallet_name,
                                   None, None, None)
        Var.wallet_handle = await wallet.open_wallet(wallet_name, None, None)

        submitter_did, _ = await signus.create_and_store_my_did(
            Var.wallet_handle, json.dumps({"seed": seed_default_steward}))

        target_did, _ = await signus.create_and_store_my_did(
                Var.wallet_handle, json.dumps({}))
        return submitter_did, target_did
    except Exception as e:
        print_error("Exception: " + str(e))


async def get_current_number_of_the_transaction():
    """
    Get the current number of transaction.

    @return: return the number of transaction.
    """
    submitter_did, target_did = await create_submitter_did()
    seqNo = 0
    try:
        nym_req = await ledger.build_nym_request(submitter_did, target_did,
                                                 None, None, None)
        response = await ledger.sign_and_submit_request(Var.pool_handle,
                                                        Var.wallet_handle,
                                                        submitter_did,
                                                        nym_req)
        seqNo = json.loads(response)['result']['seqNo']
        print_green("Current number of transactions: " + str(seqNo))
        return seqNo
    except Exception as e:
        print_error("Exception: " + str(e))


async def get_a_transaction_by_seqNo(seqNo):
    """
    Get the transaction by number.

    @param seqNo: The seqNo of the transaction.
                   That will be used to get transaction information.
    @return: return the transaction information.
    """
    submitter_did, _ = await create_submitter_did()

    get_txn_request = await ledger.build_get_txn_request(submitter_did,
                                                         int(seqNo))
    result = await ledger.sign_and_submit_request(Var.pool_handle,
                                                  Var.wallet_handle,
                                                  submitter_did,
                                                  get_txn_request)
    return result


async def calculate_transactions_per_minute(start_seqNo, end_seqNo):
    """
    Calculating the transactions per minute by getting the begin transaction
    and the current transaction.
    Then it shows the number of transactions per minute, second.

    @param start_seqNo: The starting seqNo of the transaction.
                   That will be used to get transaction information.
    @param end_seqNo: The ending seqNo of the transaction.
                   That will be used to get transaction information.
    """
    try:
        # get time of the begin transaction
        start_number = int(start_seqNo)
        begin_trans = await get_a_transaction_by_seqNo(start_number)
        begin_time = int(json.loads(begin_trans)['result']['data']['txnTime'])

        # get number and time of the latest transaction
        if not end_seqNo:
            latest_number = await get_current_number_of_the_transaction() - 1
        else:
            latest_number = int(end_seqNo)
        latest_trans = await get_a_transaction_by_seqNo(latest_number)
        latest_time = int(json.loads(latest_trans)['result']['data']['txnTime'])

        # calculate the transactions per second
        num_of_trans = latest_number - int(start_number)
        duration_as_second = latest_time - begin_time
        duration_as_minute = (latest_time - begin_time)/60
        result_minute = num_of_trans / duration_as_minute
        result_second = num_of_trans / duration_as_second
        print_green("From number: " + str(start_number) + " - Timestamp: "
                    + str(begin_time))
        print_green("To number: " + str(latest_number) + " - Timestamp: "
                    + str(latest_time))
        print_green("ADD measurement")
        print_green(str(int(result_minute)) + " txns/min")
        print_green(str(int(result_second)) + " txns/sec")
    except Exception as e:
        print("Exception: " + str(e))


if __name__ == '__main__':
    args = Options().args
    try:
        loop = get_event_loop()
        if args.count:
            loop.run_until_complete(get_current_number_of_the_transaction())
        elif args.start_seqNo:
                loop.run_until_complete(
                    calculate_transactions_per_minute(
                        args.start_seqNo, args.end_seqNo))
        loop.close()
    except Exception as e:
        print("Exception: " + str(e))
