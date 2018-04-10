#! /usr/bin/env python3
import os
import sys
import json
import asyncio
import time
import logging.handlers
from indy import ledger, signus, wallet, pool
from indy.error import IndyError
import argparse
import random as Rand

# Run this script to process output from the .txt output from Perf_Add_nyms.py or the add_nyms.py file.  This script will
# run the get_nym command on all the NYMs found in the .txt output files.  The .txt files that used by this script should
# be stored in a subdirectory in the same location this script is running from.  The command line options allow the user to
# specify the location of the text files to process, the location of the genesis transaction file and the name
# of the genesis transaction file.  If these options are not specified, default values will be used.

# Examples:
# specify the location for a genesis transaction file:
#   python3.6 Perf_get_nyms.py -t ~/PycharmProjects/multithread/stability_pool
# specify the directory name that contains the NYM files to process:
#     python3.6 Perf_get_nyms.py -d /home/devone/PycharmProjects/multithread
# specify the name of the genesis transaction file:
#     python3.6 Perf_get_nyms.py -g test_file

# -------------------------------------------------------------------------------

#  1. open a directory containing the nym files (os.chdir(args.d)) - change to the directory
#  1a enter the directory on the command line
#   use default trusteeID, default wallet
#  2. Read the files and make a get nym request (look for anything with .txt and addnyms in the filename)
# NOTTODO: 2a Create a couple of threads to process the reads
#  3. Use random times to pause between file reads and random numer of files to read
#  4. record start time, end time and total number of NYMs.  Record how long it takes to process the reads per nym,
# NOTTODO:  Might need pool_name, key_to_use, threadnum on the command line
#  Write the results and summary output to a log file
#  write the number of nyms submitted to the log
#  write the time it took to process the nyms to the log

parser = argparse.ArgumentParser(description='Script to feed multiple NYMs from files created by '
                                             'the \'Perf_Add_nyms.py\'')

parser.add_argument('-d', help='Specify the directory that contains the .txt files with NYMs.  The default '
                               'directory is set to the "nym_files" directory in the scripts current working '
                               'directory.', action='store', default=os.path.join(os.getcwd(), "limited"))

parser.add_argument('-t', help='Location and name of genesis transaction file.  The default is set to the '
                               'root of the users home directory.', action='store', default=os.path.expanduser("~"))

parser.add_argument('-g', help='Specify the name of the genesis transaction file.  The default name will be '
                               '\"stability_pool\"', action='store', default='stability_pool_no_blskey')

parser.add_argument('-b', help='To see additional output, set debug output to true', action='store_true', default=False)

parser.add_argument('-s', help='Specify the number of threads (required when using the Perf_runner.py script) '
                               'The default value will be 1', action='store', type=int, default=1)
results = parser.parse_args()

# Create the log name
# ----------------------------------------------------------------------------------------------------------------------
log_tm = time.strftime("%d-%m-%Y_%H-%M-%S")
log_name = repr(results.s) + '-Perf_get_nymm_' + log_tm + '.log'

# Setup logger with an output level
logger = logging.getLogger('Perf_get_nym_log')
logger.setLevel(logging.INFO)

# Add the log message handler to the logger, set the max size for the log and the count for splitting the log
handler = logging.handlers.RotatingFileHandler(
    log_name, maxBytes=5000000, backupCount=10)
logger.addHandler(handler)


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

    nym_counter = 0
    total_number_of_nyms = 0
    file_count = 0
    my_wallet_handle = 0
    pool_handle = 0
    files = []
    time_results = []
    debug = results.b
    pool_name = "get_nym_pool"
    wallet_name = "get_nym_wallet"
    key_to_use = '000000000000000000000000Steward1'
    # creds = json.dumps({'authorization': 'test'})
    creds = None
    show_the_time = ""
    # nym_values = []
    # use_file = False


class Timer:
    """  Timer to track the overall time it takes to process all the NYMs.  Added show_the_time variable to put
    the time in a log for each individual NYM"""
    def __init__(self):
        self.start = time.time()

    def endtime(self):
        # Stop the timer after the file is processed, store the time in a list
        test_elapsed_time = time.time() - self.start
        MyVariables.time_results.append(test_elapsed_time)
        MyVariables.show_the_time = test_elapsed_time


def create_file_list():
    """ Collect all the .txt files in the specified directory and store them in a list """

    file_list = os.listdir(results.d)
    file_list.sort()
    for x in file_list:
        if x.endswith(".txt"):
            if MyVariables.debug:
                print(x)
            MyVariables.files.append(x)


async def get_nyms(threadnum):
    """  Process to run the Ger NYMs command """

    if MyVariables.debug:
        print("\n\n--------------------------------------------------------------------")
        print("Pool name: %s" % MyVariables.pool_name)
        print("Key to use: %s" % str(MyVariables.key_to_use))
        print("Directory to use: " + results.d)
        print("Path to genesis transaction file: " + str(results.t))
        print("Genesis transaction file name: " + str(results.g))
        print("--------------------------------------------------------------------")
        # print("Thread Number %d" % repr(threadnum))
        # input("Wait.........")

    # Create ledger config from genesis txn file
    # ------------------------------------------------------------------------------------------------------------------
    # Combine the path and the name of the genesis transaction file
    # pool_genesis_txn_path = os.path.join(results.t, results.g)
    pool_genesis_txn_path = 'pool_transactions_genesis'
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})

    if MyVariables.debug:
        print(Colors.OKBLUE + "\n\t---Genesis transaction file path and filename " + Colors.ENDC +
              repr(pool_genesis_txn_path))
        input("Wait.........")

    try:
        await pool.create_pool_ledger_config(MyVariables.pool_name, pool_config)
        print(Colors.HEADER + "\n\t======== Created ledger config from genesis txn file" + Colors.ENDC)
    except IndyError as e:
        if e.error_code == 306:
            print(Colors.FAIL + "The ledger already exists, moving on..." + Colors.ENDC)
        else:
            raise

    # Open pool ledger
    # ------------------------------------------------------------------------------------------------------------------
    try:
        pool_handle = await pool.open_pool_ledger(MyVariables.pool_name, None)
        MyVariables.pool_handle = pool_handle

        print(Colors.HEADER + "\n\t======== Opened pool ledger %s" % str(pool_handle) + Colors.ENDC)
    except IndyError as e:
        print(Colors.FAIL + "Failed to create pool handle" + Colors.FAIL)
        print(Colors.FAIL + str(e) + Colors.ENDC)
        sys.exit(666)

    # Create My Wallet and Get Wallet Handle
    # ------------------------------------------------------------------------------------------------------------------
    try:
        await wallet.create_wallet(MyVariables.pool_name, MyVariables.wallet_name, None, None, MyVariables.creds)
        print(Colors.HEADER + "\n\t======== Created wallet" + Colors.ENDC)
    except IndyError as e:
        if e.error_code == 203:
            print(Colors.FAIL + ("Wallet '%s' already exists.  Skipping wallet creation..." %
                                 str(MyVariables.pool_name)) + Colors.ENDC)
        else:
            raise

    # Open the wallet
    # ------------------------------------------------------------------------------------------------------------------
    try:
        my_wallet_handle = await wallet.open_wallet(MyVariables.wallet_name, None, MyVariables.creds)
        MyVariables.my_wallet_handle = my_wallet_handle
        print(Colors.HEADER + "\n\t======== Opened wallet" + Colors.ENDC)
    except IndyError as e:
        print(Colors.FAIL + str(e) + Colors.ENDC)

    if MyVariables.debug:
        print("Wallet:  %s" % str(my_wallet_handle))

    await asyncio.sleep(0)

    # Create the DID to use
    # ------------------------------------------------------------------------------------------------------------------
    try:
        steward_did = await signus.create_and_store_my_did(my_wallet_handle, json.dumps({"seed":
                                                                                        MyVariables.key_to_use}))
        print(Colors.HEADER + "\n\n\t======== Created DID to use when verifying NYMS %s " % str(steward_did[0]) + Colors.ENDC)
        logger.info("\n\n\t======== Created DID to use when verifying NYMS %s " % str(steward_did[0]))
    except IndyError as e:
        print(Colors.FAIL + str(e) + Colors.ENDC)
        sys.exit(2)

    # Read the files  into a list for processing
    # ------------------------------------------------------------------------------------------------------------------
    # Start processing the file list
    while len(MyVariables.files) > 0:
        if MyVariables.debug:
            print("Started loop")

        # Pick a random number of files to process
        if len(MyVariables.files) >= 10:
            number_of_files_to_process = Rand.randint(5, 10)
        else:
            number_of_files_to_process = Rand.randint(1, len(MyVariables.files))

        # Run the get_nym command for each NYM from each file selected until the list is empty
        print(Colors.HEADER + "\n\nNumber of files in the list to process %d" % len(MyVariables.files) + Colors.ENDC)
        logger.info("--Number of files in the list to process %d" % len(MyVariables.files))

        for _ in range(number_of_files_to_process):
            MyVariables.nym_counter += 1    # Display to show how many files are currently getting processed

            # Pick a random file using the index value
            file_name = Rand.choice(range(len(MyVariables.files)))
            print(Colors.HEADER + "\nProcessing file: #" + repr(MyVariables.nym_counter) + Colors.ENDC + ".'" +
                  MyVariables.files[file_name] + "'\n")

            # Read the file and process each NYM
            path_to_file = os.path.join(results.d, MyVariables.files[file_name])
            if MyVariables.debug:
                print(Colors.OKBLUE + "\n\t--Path and file to process --\n\t\t" + repr(path_to_file) + Colors.ENDC)

            try:
                open_file = open(path_to_file, 'r')
                MyVariables.file_count += 1
            except IOError as e:
                print(Colors.FAIL + str(e) + Colors.ENDC)
                sys.exit(1)

            # Iterate through each line and make the call to get the NYM
            for line in open_file:
                line = line.strip()
                if MyVariables.debug:
                    print("\n\t\tDID:  " + line)

                get_nym_txn1 = await ledger.build_get_nym_request(steward_did[0], line)
                print(Colors.HEADER + "\n\t======== Get the NYM transaction for " + Colors.ENDC + repr(line) +
                      " from file \"" + MyVariables.files[file_name] + "\" \n\n")
                await asyncio.sleep(0)

                try:
                    # Start the timer per NYM to process
                    mytimer = Timer()

                    get_nym_txn_resp = await ledger.submit_request(MyVariables.pool_handle, get_nym_txn1)
                    MyVariables.total_number_of_nyms += 1
                    print(Colors.HEADER + "\t======== Submit request response:  %s" % str(get_nym_txn_resp) + Colors.ENDC)
                except IndyError as e:
                    print(Colors.FAIL + str(e) + Colors.ENDC)

                # Stop the timer after the file is processed
                mytimer.endtime()

                logger.info("\n======== DID: " + repr(line))
                logger.info("======== Processed in %s seconds" % MyVariables.show_the_time)

            open_file.close()

            # Remove the file from the list
            MyVariables.files.pop(file_name)

        # If there are files in the list, run the timer...
        if MyVariables.files:
            # await asyncio.sleep(Rand.randint(5, 8))

            logger.info("\nNumber of files left in list: %d" % len(MyVariables.files))
            logger.info("Number of files processed:  %d" % MyVariables.file_count)
            logger.info("Running total of NYMs processed: %d" % MyVariables.total_number_of_nyms + "\n")

            # Run the timer delay between files
            # timer()

        # # Run the timer between files
        # timer()
    else:
        print(Colors.HEADER + "Finished processing files" + Colors.ENDC)
        # Clean up
        # --------------------------------------------------------------------------------------------------------------
        try:
            print(Colors.HEADER + "\n\t======== Close the pool ledger and wallet..." + Colors.ENDC)
            await pool.close_pool_ledger(MyVariables.pool_handle)
            await wallet.close_wallet(MyVariables.my_wallet_handle)
        except IndyError as e:
            print(Colors.FAIL + str(e) + Colors.ENDC)

        # Run the cleanup
        # clean_up()


def timer():
    """  Timed delay between calls to run the script  """

    watch_time = 0
    overwrite = 0
    timer_seconds = 10  # Testing
    # timer_seconds = Rand.randint(245, 700)  # 180 = 3min, 300 seconds = 5min, 900 seconds = 15min
    while watch_time < timer_seconds:
        time.sleep(1)
        watch_time += 1
        remain_time = timer_seconds - watch_time
        #  if remain_time <= x <= end:
        if remain_time < 100 and remain_time > 9:
            remain_time = int("0") + remain_time
        if remain_time < 10:
            remain_time = int("00") + remain_time
        sys.stdout.write("Countdown to next call: %s%s \r" % (str(remain_time), " " * overwrite))
        sys.stdout.flush()


def clean_up():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
    import shutil

    print("\n\tCheck if the wallet and pool for this test exist and delete them...\n")
    x = os.path.expanduser('~')
    work_dir = x + os.sep + ".indy_client"

    try:
        shutil.rmtree(work_dir + "/pool/" + MyVariables.pool_name)
    except IOError as E:
        print(str(E))

    try:
        shutil.rmtree(work_dir + "/wallet/" + MyVariables.wallet_name)
    except IOError as E:
        print(str(E))

    print("Finished deleting wallet and pool folders in " + repr(work_dir))

#########################################################################################
# --------------------------
#           MAIN
# --------------------------


loop = asyncio.get_event_loop()

# Create the file list to process
create_file_list()

# Start the timer to track how long it takes to run the test
start_time = time.time()

# Start the method
loop.run_until_complete(get_nyms(results.s))

# Clean up
# clean_up()

# Stop the timer after the test is complete
elapsed_time = time.time() - start_time

# Format the time display to look nice
hours = elapsed_time / 3600
elapsed_time = 3600 * hours
minutes = elapsed_time / 60
seconds = 60 * minutes

if MyVariables.file_count == 0:
    print(Colors.FAIL + "\n\nThe files containing NYMs to process was not found.  Please specify the "
                        "correct location for the NYM files.  Use the -h for more information" + Colors.ENDC)
    clean_up()
    sys.exit(1)

sum_of_time = sum(MyVariables.time_results)
average_time_per_file = sum_of_time / MyVariables.file_count
nyms_per_second = MyVariables.total_number_of_nyms / sum_of_time

logger.info("\n------ Processed a total of %d NYMS from %d files" % (MyVariables.total_number_of_nyms,
                                                                     MyVariables.file_count))
logger.info("------ Average time per file in seconds {average_time_per_file:.2f}")
logger.info("------ Number of NYMs per second {nyms_per_second:.2f}")
logger.info("------ Total Elapsed time: %dh:%dm:%ds" % (hours, minutes, seconds) + " ------")
