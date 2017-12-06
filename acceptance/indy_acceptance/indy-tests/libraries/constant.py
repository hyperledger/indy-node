
"""
Created on Nov 9, 2017

@author: khoi.ngo

Containing all constants that are necessary to execute test scenario.
"""


class Colors:
    """
    Class to set the colors for text.
    Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC)
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color.
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Roles:
    """
    Class to define roles.
    """
    TRUSTEE = "TRUSTEE"
    STEWARD = "STEWARD"
    TRUST_ANCHOR = "TRUST_ANCHOR"
    TGB = "TGB"  # obsolete.
    NONE = ""


class Constant:
    """
    Class Constant store some necessary paths.
    """
    import os
    user_home = os.path.expanduser('~') + os.sep
    work_dir = user_home + ".indy"
    seed_default_trustee = "000000000000000000000000Trustee1"
    # The path to the genesis transaction file is configurable. The default directory is "/var/lib/indy/sandbox/".
    genesis_transaction_file_path = "/var/lib/indy/sandbox/"
    pool_genesis_txn_file = genesis_transaction_file_path + "pool_transactions_sandbox_genesis"
    domain_transactions_sandbox_genesis = genesis_transaction_file_path + "domain_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = genesis_transaction_file_path + "original_pool_transactions_sandbox_genesis"


class Message:
    ERR_PATH_DOES_NOT_EXIST = "Cannot find the path specified! \"{}\""
    ERR_CANNOT_FIND_ANY_TEST_SCENARIOS = "Cannot find any test scenarios!"
    ERR_TIME_LIMITATION = "Aborting test scenario because of time limitation!"
    ERR_COMMAND_ERROR = "Invalid command!"
    INFO_RUNNING_TEST_POS_CONDITION = "Running clean up for aborted test scenario."
    INFO_ALL_TEST_HAVE_BEEN_EXECUTED = "All test have been executed!"
    INDY_ERROR = "IndyError: {}"
    EXCEPTION = "Exception: {}"
