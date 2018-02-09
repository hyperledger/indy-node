#! /usr/bin/env python3
import os
import sys
import json
import asyncio
import time
import argparse
import logging.handlers
from indy import ledger, signus, wallet, pool
from indy.error import IndyError


# The genesis pool transaction file  and the script (Perf_Add_nyms.py) should both
# be in the same directory.
# To run, make sure to pass the key to use when creating the DIDs, for
# example: python3.6 Perf_Add_nyms.py testPool 100 TestAddNodeWithTrustAnchor000001
#          python3.6 Perf_Add_nyms.py testPool 500 000000000000000000000000Steward1 <number_of_threads>
# -------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Script to create multiple NYMs and store them in .txt files to be  '
                                             'used by the \'Perf_get_nyms.py\' script.\n\n', usage='To create 500 '
                                             'NYMs in the default \'nym_files\' directory and use \nthe default '
                                             '\'stability_pool\' transaction file in the current working directory, '
                                             '\nuse: python3.6 Perf_Add_nyms.py -p testPool -n 500 -i 000000000000000000000000Steward1 -s 1')

parser.add_argument('-d', help='Specify the directory location to store the NYM .txt files.  The default '
                               'directory is set to the "nym_files" directory in this scripts current working '
                               'directory.', action='store', default=os.path.join(os.getcwd(), "nym_files"))

parser.add_argument('-t', help='Location of the genesis transaction file.  The default is set to this '
                               'scripts current working directory.', action='store', default=os.path.expanduser("~"))

parser.add_argument('-g', help='Specify the name of the genesis transaction file.  The default name will be '
                               '\"stability_pool\"', action='store', default='stability_pool_no_blskey')

parser.add_argument('-p', help='Specify the pool name to use.  The default name will be \"Perf_Add_NYMS\"',
                    action='store', default='Perf_Add_NYMS')

parser.add_argument('-n', help='Specify the number of NYMs tp create.  The default value will be 100',
                    action='store', type=int, default=100)

parser.add_argument('-i', help='Specify the role to use to create the NYMs.  The default steward ID will be  used',
                    action='store', default='000000000000000000000000Steward1')

parser.add_argument('-s', help='Specify the number of threads (required when using the Perf_runner.py script) '
                               'The default value will be 1', action='store', type=int, default=1)

parser.add_argument('-b', help='To see additional output, use -b in addition to the other command line options',
                    action='store_true', default=False)
# parser.print_help()
results = parser.parse_args()
# default=os.path.join(os.getcwd(), "nym_files"))


class Colors:
    """ Class to set the colors for text.  Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MyVariables:
    """  Needed some global variables. """

    nym_counter = 1
    nym_values = []
    use_file = True
    debug = results.b
    my_wallet_handle = 0
    pool_handle = 0
    pool_name = results.p


async def add_nyms(pool_name, nyms_to_run, key_to_use, threadnum):
    # Setup logger with an output level, creates the .txt file that will contain all the NYMs
    # ------------------------------------------------------------------------------------------------------------------
    tm = time.strftime("%d-%m-%Y_%H-%M-%S")
    log_name = os.path.join(os.getcwd(), results.d + os.sep + (repr(threadnum) + "-addnyms_" + tm + ".txt"))

    logger = logging.getLogger('Perf_Add_nyms')
    logger.setLevel(logging.INFO)

    # Add the log message handler to the logger, set the max size for the log and the count for splitting the log
    handler = logging.handlers.RotatingFileHandler(
        log_name, maxBytes=5000000, backupCount=500)
    logger.addHandler(handler)

    # 1. Create ledger config from genesis txn file
    # pool_genesis_txn_path = os.path.expanduser("~") + "/PycharmProjects/.sdktesting/pool_transactions_sandbox_" \
    #                                                   "genesis_blskey"
    # pool_genesis_txn_path = os.path.join(results.t, results.g)
    pool_genesis_txn_path = 'pool_transactions_genesis'
    # pool_genesis_txn_path = 'pool_transactions_sandbox_genesis'
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})

    if MyVariables.debug:
        print("Pool name: %s" % pool_name)
        print("Number of NYMs to create: %s" % str(nyms_to_run))
        print("Key to use %s" % str(key_to_use))
        print("Thread Number %d" % threadnum)
        print("Where the NYMs are stored: " + repr(log_name))
        print("Name and location of the genesis file: " + pool_genesis_txn_path)
        input("Wait.........")

    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
        print(Colors.HEADER + "\n\n\t======== Created ledger config from genesis txn file" + Colors.ENDC)
    except IndyError as e:
        if e.error_code == 306:
            print(Colors.FAIL + "The ledger already exists, moving on..." + Colors.ENDC)
            # print(Colors.FAIL + str(e) + Colors.ENDC)
        else:
            raise

    # 2. Open pool ledger
    try:
        pool_handle = await pool.open_pool_ledger(pool_name, None)
        MyVariables.pool_handle = pool_handle
        print(Colors.HEADER + "\t======== Opened pool ledger %s" % str(pool_handle) + Colors.ENDC)
        # input(Colors.WARNING + "\n\nPoolHandle is %s" % str(pool_handle) + Colors.ENDC)
    except IndyError as e:
        print(Colors.FAIL + str(e) + Colors.ENDC)

    # 3. Create My Wallet and Get Wallet Handle
    try:
        await wallet.create_wallet(pool_name, "add_nyms_wallet", None, None, None)
        print(Colors.HEADER + "\t======== Created wallet" + Colors.ENDC)
    except IndyError as e:
        if e.error_code == 203:
            print(Colors.FAIL + ("Wallet '%s' already exists.  Skipping wallet creation..." % str(pool_name)) +
                  Colors.ENDC)
        else:
            raise

    try:
        my_wallet_handle = await wallet.open_wallet('add_nyms_wallet', None, None)
        MyVariables.my_wallet_handle = my_wallet_handle
        print(Colors.HEADER + "\t======== Opened wallet" + Colors.ENDC)
    except IndyError as e:
        print(Colors.FAIL + str(e) + Colors.ENDC)

    # input(Colors.WARNING + "\n\nWallet handle is %s" % str(my_wallet_handle) + Colors.ENDC)

    if MyVariables.debug:
        print("Wallet:  %s" % str(my_wallet_handle))

    # 4.5 Create and Send DID
    # Add signing key to wallet (This is who will be adding NYMs to the ledger)
    try:
        their_did = await signus.create_and_store_my_did(my_wallet_handle, json.dumps({"seed": key_to_use}))
        print(Colors.HEADER + "\n\n\t======== Created DID to use when adding NYMS %s " % str(their_did) + Colors.ENDC)
    except IndyError as e:
        print(Colors.FAIL + str(e) + Colors.ENDC)

    if MyVariables.debug:
        print("Their DID: %s" % (str(their_did)))

    # Create new DID to add to ledger
    while MyVariables.nym_counter <= int(nyms_to_run):
        try:
            # Create new DID, my_pk was removed from tuple
            (my_did, my_verkey) = await signus.create_and_store_my_did(my_wallet_handle, "{}")
            print(Colors.HEADER + "\t========  DID%i: %s " % (MyVariables.nym_counter, str(my_did) + Colors.ENDC))

            if MyVariables.use_file:
                # Write the DID to the file
                logger.info(my_did)

            # Create NYM Request
            nym_txn_req = await ledger.build_nym_request(their_did[0], my_did, None, None, None)
            print(Colors.HEADER + "\t======== Created NYM request..." + Colors.ENDC)

            # Send NYM to ledger
            await ledger.sign_and_submit_request(MyVariables.pool_handle, my_wallet_handle, their_did[0], nym_txn_req)
            print(Colors.HEADER + "\t======== Submitted NYM request" + Colors.ENDC)

            MyVariables.nym_counter += 1

        except IndyError as e:
            print(Colors.FAIL + str(e) + Colors.ENDC)
            sys.exit(1)

    print(Colors.HEADER + "\t========  Finished" + Colors.ENDC)

#########################################################################################
# --------------------------
#           MAIN
# --------------------------
# print("Sent: " + repr(sys.argv[1:]))
# if len(sys.argv) != 5:
#     print("Usage: %s <poolname(no spaces)> <Number of NYMs to create> <truestee/steward Seed> <thread#>" %
#           (sys.argv[0]))
#     sys.exit(2)

loop = asyncio.get_event_loop()

# Start the timer to track how long it takes to run the test
start_time = time.time()
# pool name to use is sys.argv1, number of transactions is sys.argv2, key to use for the transactions is sys.argv3
loop.run_until_complete(add_nyms(results.p, results.n, results.i, results.s))

# Stop the timer after the test is complete
elapsed_time = time.time() - start_time

# Format the time display to look nice
hours = elapsed_time / 3600
elapsed_time = 3600 * hours
minutes = elapsed_time / 60
seconds = 60 * minutes
# print("\n------ Elapsed time: %dh:%dm:%ds" % (hours, minutes, seconds) + " ------")

# Example syntax:
# python3.6 add_nyms.py testPool 500 000000000000000000000000Steward1 number_of_threads
#          |     0     |    1   | 2 |           3                             4
