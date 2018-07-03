import os   # noqa
import importlib    # noqa
import sys
from importlib.util import module_from_spec, spec_from_file_location    # noqa: E402

import pip

import indy_node.server.plugin     # noqa: E402

from indy_common.config_util import getConfigOnce   # noqa: E402
from plenum import find_and_load_plugin

PLUGIN_LEDGER_IDS = set()
PLUGIN_CLIENT_REQUEST_FIELDS = {}
PLUGIN_CLIENT_REQ_OP_TYPES = {}


def setup_plugins():
    # TODO: Refactor to use plenum's setup_plugins
    # TODO: Should have a check to make sure no plugin defines any conflicting ledger id or request field
    global PLUGIN_LEDGER_IDS
    global PLUGIN_CLIENT_REQUEST_FIELDS
    global PLUGIN_CLIENT_REQ_OP_TYPES

    config = getConfigOnce(ignore_external_config_update_errors=True)

    plugin_root = config.PLUGIN_ROOT
    try:
        plugin_root = importlib.import_module(plugin_root)
    except ImportError:
        raise ImportError('Incorrect plugin root {}. No such package found'.
                          format(plugin_root))
    sys.path.insert(0, plugin_root.__path__[0])
    enabled_plugins = config.ENABLED_PLUGINS
    installed_packages = {p.project_name: p for p in pip.get_installed_distributions()}
    for plugin_name in enabled_plugins:
        plugin = find_and_load_plugin(plugin_name, plugin_root, installed_packages)
        plugin_globals = plugin.__dict__
        # The following lines are idempotent so loading the same plugin twice is not the problem.
        if 'LEDGER_IDS' in plugin_globals:
            PLUGIN_LEDGER_IDS.update(plugin_globals['LEDGER_IDS'])
        if 'CLIENT_REQUEST_FIELDS' in plugin_globals:
            PLUGIN_CLIENT_REQUEST_FIELDS.update(plugin_globals['CLIENT_REQUEST_FIELDS'])
        if 'REQ_OP_TYPES' in plugin_globals:
            PLUGIN_CLIENT_REQ_OP_TYPES.update(plugin_globals['REQ_OP_TYPES'])

    # Reloading message types since some some schemas would have been changed
    import indy_common.types
    importlib.reload(indy_common.types)


setup_plugins()


from .__metadata__ import *  # noqa
