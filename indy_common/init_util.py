from plenum.common.init_util import initialize_node_environment as \
    p_initialize_node_environment, cleanup_environment
from indy_common.config_util import getConfig


def initialize_node_environment(name, base_dir, sigseed=None,
                                override_keep=False,
                                config=None):
    config = config or getConfig()
    base_dir = base_dir or config.baseDir
    cleanup_environment(name, base_dir)
    vk, bls_key = p_initialize_node_environment(name, base_dir, sigseed, override_keep)

    return vk, bls_key
