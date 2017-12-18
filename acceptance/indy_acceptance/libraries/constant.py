
"""
Created on Nov 9, 2017

@author: khoi.ngo

Containing all constants that are necessary to execute test scenario.
"""
import os
from enum import Enum


class Color(str, Enum):
    """
    Class to set the colors for text.
    Syntax:  print(Color.OKGREEN +"TEXT HERE" +Color.ENDC)
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color.
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Role(str, Enum):
    """
    Class to define roles.
    """
    TRUSTEE = "TRUSTEE"
    STEWARD = "STEWARD"
    TRUST_ANCHOR = "TRUST_ANCHOR"
    TGB = "TGB"  # obsolete.
    NONE = ""


work_dir = os.path.expanduser('~') + os.sep + ".indy"
seed_default_trustee = "000000000000000000000000Trustee1"
# The path to the genesis transaction file is configurable. The default
# directory is "/var/lib/indy/sandbox/".
genesis_transaction_file_path = "/var/lib/indy/sandbox/"
pool_genesis_txn_file = genesis_transaction_file_path + \
    "pool_transactions_sandbox_genesis"
original_pool_genesis_txn_file = genesis_transaction_file_path + \
    "original_pool_transactions_sandbox_genesis"

# Message
ERR_PATH_DOES_NOT_EXIST = "Cannot find the path specified! \"{}\""
INDY_ERROR = "IndyError: {}"
EXCEPTION = "Exception: {}"
