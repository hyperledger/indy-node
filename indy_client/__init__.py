import os
import indy_client

from indy_client.agent.jsonpickle_util import setUpJsonpickle
from indy_client.client.wallet.migration import migrate_indy_wallet_raw

from indy_common.plugin_helper import writeAnonCredPlugin
from plenum.client.wallet import WALLET_RAW_MIGRATORS

BASE_DIR = os.path.join(os.path.expanduser("~"), ".indy")
writeAnonCredPlugin(BASE_DIR)

# This is to setup anoncreds wallet related custom jsonpickle handlers to
# serialize/deserialize it properly
setUpJsonpickle()

WALLET_RAW_MIGRATORS.append(migrate_indy_wallet_raw)
