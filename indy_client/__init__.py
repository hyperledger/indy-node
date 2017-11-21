import os
import indy_client

from indy_client.agent.jsonpickle_util import setUpJsonpickle
from indy_client.client.wallet.migration import migrate_indy_wallet_raw

from indy_common.plugin_helper import writeAnonCredPlugin
from plenum.client.wallet import WALLET_RAW_MIGRATORS
from indy_common.config_util import getConfig

config = getConfig()
BASE_DIR = os.path.expanduser(config.CLI_BASE_DIR)
writeAnonCredPlugin(BASE_DIR)

# This is to setup anoncreds wallet related custom jsonpickle handlers to
# serialize/deserialize it properly
setUpJsonpickle()

WALLET_RAW_MIGRATORS.append(migrate_indy_wallet_raw)
