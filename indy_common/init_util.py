from plenum.common.init_util import initialize_node_environment as \
    p_initialize_node_environment, cleanup_environment


def initialize_node_environment(name, node_config_helper, sigseed=None,
                                override_keep=False):
    cleanup_environment(node_config_helper.ledger_dir)
    vk, bls_key, key_proof = p_initialize_node_environment(name, node_config_helper, sigseed, override_keep)

    return vk, bls_key, key_proof
