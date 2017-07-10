import os
import sovrin_client

from sovrin_client.agent.jsonpickle_util import setUpJsonpickle

from sovrin_common.plugin_helper import writeAnonCredPlugin
BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
writeAnonCredPlugin(BASE_DIR)

# This is to setup anoncreds wallet related custom jsonpickle handlers to
# serialize/deserialize it properly
setUpJsonpickle()