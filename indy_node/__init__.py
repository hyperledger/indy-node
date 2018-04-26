import os   # noqa
import importlib    # noqa
from importlib.util import module_from_spec, spec_from_file_location    # noqa: E402

import indy_node.server.plugin     # noqa: E402

from indy_common.config_util import getConfigOnce   # noqa: E402

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
    enabled_plugins = config.ENABLED_PLUGINS
    for plugin_name in enabled_plugins:
        plugin_path = os.path.join(plugin_root.__path__[0],
                                   plugin_name, '__init__.py')
        spec = spec_from_file_location('__init__.py', plugin_path)
        init = module_from_spec(spec)
        spec.loader.exec_module(init)
        plugin_globals = init.__dict__
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
