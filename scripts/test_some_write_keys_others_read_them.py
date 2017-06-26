"""
Test performing the following scenarios on behalf of multiple users in parallel:
- some users cyclically update their own verkeys,
- other users cyclically read verkeys of the former users.

To run the test execute this python script providing the following parameters:
-w <NUMBER_OF_USERS_UPDATING_VERKEYS> or --writers <NUMBER_OF_USERS_UPDATING_VERKEYS>
-r <NUMBER_OF_USERS_READING_VERKEYS> or --readers <NUMBER_OF_USERS_READING_VERKEYS>
-i <NUMBER_OF_ITERATIONS> or --iterations <NUMBER_OF_ITERATIONS>
-t <TIMEOUT_IN_SECONDS> or --timeout <TIMEOUT_IN_SECONDS> (optional parameter)

Examples:

python test_some_write_keys_others_read_them.py -w 2 -r 8 -i 10 -t 30

python test_some_write_keys_others_read_them.py --writers 4 --readers 20 --iteration 50
"""

import argparse
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor

from stp_core.common.log import getlogger

from sovrin_node.utils.user_scenarios import generateNymsData, \
    NymsCreationScenario, KeyRotationScenario, ForeignKeysReadScenario

STEWARD1_SEED = b"000000000000000000000000Steward1"

logger = getlogger()


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--writers",
                        action="store",
                        type=int,
                        dest="writers",
                        help="number of writers")

    parser.add_argument("-r", "--readers",
                        action="store",
                        type=int,
                        dest="readers",
                        help="number of readers")

    parser.add_argument("-i", "--iterations",
                        action="store",
                        type=int,
                        dest="iterations",
                        help="number of iterations")

    parser.add_argument("-t", "--timeout",
                        action="store",
                        type=int,
                        dest="timeout",
                        help="timeout in seconds")

    return parser.parse_args()


def main(args):
    numOfWriters = args.writers
    numOfReaders = args.readers
    numOfIterations = args.iterations
    timeout = args.timeout

    writers = generateNymsData(numOfWriters)
    readers = generateNymsData(numOfReaders)

    with ProcessPoolExecutor(numOfWriters + numOfReaders) as executor:
        usersIdsAndVerkeys = [(user.identifier, user.verkey)
                              for user in writers + readers]

        nymsCreationScenarioFuture = \
            executor.submit(NymsCreationScenario.runInstance,
                            seed=STEWARD1_SEED,
                            nymsIdsAndVerkeys=usersIdsAndVerkeys)

        nymsCreationScenarioFuture.result(timeout=timeout)
        logger.info("Created {} nyms".format(numOfWriters + numOfReaders))

        keyRotationScenariosFutures = \
            [executor.submit(KeyRotationScenario.runInstance,
                             seed=writer.seed,
                             iterations=numOfIterations)
             for writer in writers]

        writersIds = [writer.identifier for writer in writers]

        foreignKeysReadScenariosFutures = \
            [executor.submit(ForeignKeysReadScenario.runInstance,
                             seed=reader.seed,
                             nymsIds=writersIds,
                             iterations=numOfIterations)
             for reader in readers]

        futures.wait(keyRotationScenariosFutures +
                     foreignKeysReadScenariosFutures,
                     timeout=timeout)

        failed = False
        for future in keyRotationScenariosFutures + \
                foreignKeysReadScenariosFutures:
            ex = future.exception(timeout=0)
            if ex:
                failed = True
                logger.exception(ex)

        if failed:
            logger.error("Scenarios of some writers or readers failed")
        else:
            logger.info("Scenarios of all writers and readers "
                        "finished successfully")


if __name__ == "__main__":
    main(parseArgs())
