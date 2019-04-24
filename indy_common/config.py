import os
import logging
from collections import OrderedDict

from indy_common.constants import LOCAL_AUTH_POLICY, CONFIG_LEDGER_AUTH_POLICY
from plenum.common.constants import ClientBootStrategy, HS_ROCKSDB, KeyValueStorageType
from plenum.config import rocksdb_default_config

nodeReg = OrderedDict([
    ('Alpha', ('127.0.0.1', 9701)),
    ('Beta', ('127.0.0.1', 9703)),
    ('Gamma', ('127.0.0.1', 9705)),
    ('Delta', ('127.0.0.1', 9707))
])

cliNodeReg = OrderedDict([
    ('AlphaC', ('127.0.0.1', 9702)),
    ('BetaC', ('127.0.0.1', 9704)),
    ('GammaC', ('127.0.0.1', 9706)),
    ('DeltaC', ('127.0.0.1', 9708))
])

GENERAL_CONFIG_DIR = '/etc/indy/'

GENERAL_CONFIG_FILE = 'indy_config.py'
NETWORK_CONFIG_FILE = 'indy_config.py'
USER_CONFIG_FILE = 'indy_config.py'

configTransactionsFile = "config_transactions"

logFilePath = "cli.log"

outFilePath = "cli_output.log"

clientBootStrategy = ClientBootStrategy.Custom

hashStore = {
    "type": HS_ROCKSDB
}

primaryStorage = None

configStateStorage = KeyValueStorageType.Rocksdb
idrCacheStorage = KeyValueStorageType.Rocksdb
attrStorage = KeyValueStorageType.Rocksdb

configStateDbName = 'config_state'
attrDbName = 'attr_db'
idrCacheDbName = 'idr_cache_db'

rocksdb_attr_db_config = rocksdb_default_config.copy()
# Change attr_db config here if you fully understand what's going on

rocksdb_idr_cache_db_config = rocksdb_default_config.copy()
# Change idr_cache_db config here if you fully understand what's going on

db_attr_db_config = rocksdb_attr_db_config
db_idr_cache_db_config = rocksdb_idr_cache_db_config

PluginsToLoad = []

# TODO: This should be in indy_node's config

# File that stores the version of the Node ran the last time it started. (It
# might be incorrect sometimes if Node failed to update the file and crashed)
lastRunVersionFile = 'last_version'

# File that stores the version of the code to which the update has to be made.
# This is used to detect if there was an error while upgrading. Once it has
# been found out that there was error while upgrading, then it can be upgraded.
nextVersionFile = 'next_version'

# Minimum time difference (seconds) between the code update of 2 nodes
MinSepBetweenNodeUpgrades = 300

upgradeLogFile = "upgrade_log"
restartLogFile = "restart_log"

lastVersionFilePath = "last_version_file"

'''
Node control utils options
'''
controlServiceHost = "127.0.0.1"
controlServicePort = "30003"

'''
logging level for agents
'''
agentLoggingLevel = logging.INFO
'''
default logging level for node
'''
logLevel = logging.INFO

INCONSISTENCY_WATCHER_NETWORK_TIMEOUT = 90

# Top level package to be updated via pool upgrade command
UPGRADE_ENTRY = 'indy-node'

ANYONE_CAN_WRITE = False

PACKAGES_TO_HOLD = ['indy-plenum', 'indy-node', 'python3-indy-crypto', 'libindy-crypto']

authPolicy = CONFIG_LEDGER_AUTH_POLICY

SCHEMA_ATTRIBUTES_LIMIT = 125
