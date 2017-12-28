#!/usr/bin/env python3
import os
import argparse
import time
import sys
from threading import Thread, Lock

global txns
global clients
clients = 100
txns = 100

#                   ==================== Notes and information ====================
# This script will run multiple instances (threaded) of the the Perf_Add_nyms.py script or the Perf_get_nyms.py. The
# command line parameters for each script are different and can be set from this script without modifying Add_nyms or
# Get_nyms scripts.
# The settings for Perf runner are 'clients' and 'txns'.  Clients is the number of threads (or client machines) to use,
# the txns indicates how many transactions will run per client (thread).  These settings are specific to Perf_runner.py
#
# The command line for both performance scripts is created in the 'command' variable found below.  The default setting
# for Perf_Add_nyms.py uses the -n and -s parameters to specify the number of threads and clients to use.  The value
# from clients is iterated through and uses 'i' to track which iteration is processing.
# The default vaiables for the Add_nyms script will be  used.  If any of the default settings for Add_nyms or Get_nyms
# needs to be modified, add the changes here to the perf runner by modifying the 'command' variable.
#                   ================================================================
# Example:
# Run Perf_Add_nyms.py:   python3.6 Perf_runner.py -a
# Run Perf_gert_nyms.py using 3 clients (threads) - by setting clients to 3:  python3.6 Perf_runner.py -g

parser = argparse.ArgumentParser(description='This script will create multiple threads of the Perf_Add_nyms.py or '
                                             'the Perf_get_nyms.py.')

parser.add_argument('-a', help='Use this parameter to start Perf_Add_nyms.py', action='store_true',
                    default=False, required=False)
parser.add_argument('-g', help='Use this parameter to start Perf_get_nyms.py', action='store_true',
                    default=False, required=False)

# parser.print_help()
results = parser.parse_args()
if results.a:
    results.a = 'Perf_Add_nyms.py'
if results.g:
    results.g = 'Perf_get_nyms.py'


def run_test(i, lock):

    print("This is a test : " + repr(results.g))
    print("This is a test : " + repr(results.a))
    if results.a:
        # The value for -n is the 'txns' variable at the top of this script
        command = 'python3 ' + results.a + ' -n ' + str(txns) + ' -s ' + repr(i)
    elif results.g:
        # The default values for -d -t and -g in get_nym will be used
        command = 'python3 ' + results.g + ' -s ' + repr(clients) + ' -d nym_files'
    else:
        print("\n\nPlease specify a script to use or run Perf_runner.py -h for additional information")
        sys.exit(1)

    with lock:
        print("Starting thread {}".format(i))

    # Run the command
    # print(command)
    os.system(command)

    with lock:
        print("Thread {} stopped".format(i))


# Create threads
lock = Lock()

# Start Time
# timeBegin = datetime.now()
overmind_start_time = time.time()

# get the number of clients (threads) to create
threads = [Thread(target=run_test, args=(i, lock)) for i in range(clients)]

# Start threads
for x in threads:
    x.start()

# Stop threads
for x in threads:
    x.join()

# Total Time
totalTime = time.time() - overmind_start_time

hours = totalTime / 3600
totalTime = 3600 * hours
minutes = totalTime / 60
seconds = 60 * minutes

ttl_txns = clients * txns
ttl_seconds = int((hours * 3600) + (minutes * 60) + seconds)
try:
    txns_per_second = int(ttl_txns / ttl_seconds)
except Exception as E:
    txns_per_second = None
    print("There is too small test run time that causes an error: ", E)

print("\n -----------  Total time to run the test: %dh:%dm:%ds" % (hours, minutes, seconds) + "  -----------")
print("\n Clients = " + str(clients))
print("\n Transaction per client = " + str(txns))
print("\n Total transactions requested = " + str(ttl_txns))
print("\n Estimated transactions per second = " + str(txns_per_second))

tm = time.strftime("%d-%m-%Y_%H-%M-%S")
file = open("test_results_time_" + tm + ".log", "w")
file.write("\n -----------  Total time to run the test: %dh:%dm:%ds" % (hours, minutes, seconds) + "  -----------\n")
file.write("\n Clients = " + str(clients))
file.write("\n Transaction per client = " + str(txns))
file.write("\n Total transactions requested = " + str(ttl_txns))
file.write("\n Estimated transactions per second = " + str(txns_per_second))
file.close()