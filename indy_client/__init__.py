import os
import indy_client

from indy_client.agent.jsonpickle_util import setUpJsonpickle

from indy_common.plugin_helper import writeAnonCredPlugin
BASE_DIR = os.path.join(os.path.expanduser("~"), ".indy")
writeAnonCredPlugin(BASE_DIR)

# This is to setup anoncreds wallet related custom jsonpickle handlers to
# serialize/deserialize it properly
setUpJsonpickle()
