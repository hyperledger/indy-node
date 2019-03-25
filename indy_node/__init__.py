from .__metadata__ import (
    __title__, __version_info__, __version__, __manifest__, __description__,
    __long_description__, __keywords__, __url__, __author__,
    __author_email__, __maintainer__, __license__,
    load_version, set_version, load_manifest, set_manifest
)

PLUGIN_LEDGER_IDS = set()
PLUGIN_CLIENT_REQUEST_FIELDS = {}
PLUGIN_CLIENT_REQ_OP_TYPES = {}


# TODO review is it really necessary here
def setup_plugins():
    import sys
    import os
    import pip
    import importlib    # noqa
    from importlib.util import module_from_spec, spec_from_file_location    # noqa: E402
    from indy_common.config_util import getConfigOnce   # noqa: E402
    import indy_node.server.plugin     # noqa: E402

    def find_and_load_plugin(plugin_name, plugin_root, installed_packages):
        if plugin_name in installed_packages:
            # TODO: Need a test for installed packages
            plugin_name = plugin_name.replace('-', '_')
            plugin = importlib.import_module(plugin_name)
        else:
            plugin_path = os.path.join(plugin_root.__path__[0],
                                       plugin_name, '__init__.py')
            spec = spec_from_file_location('__init__.py', plugin_path)
            plugin = module_from_spec(spec)
            spec.loader.exec_module(plugin)

        return plugin

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


try:
    import packaging
except ImportError:
    pass  # it is expected in raw env
else:
    setup_plugins()
