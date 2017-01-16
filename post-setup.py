import os

from sovrin_common.setup_util import Setup

BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
Setup(BASE_DIR).setupTxns()