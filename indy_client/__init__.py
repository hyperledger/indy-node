#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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
