from indy_node.server.plugin.agent_authz.cache import AgentAuthzCommitmentCache
from plenum.persistence.storage import initKeyValueStorage


def get_authz_commitment_cache(data_dir, name, config):
    return AgentAuthzCommitmentCache(initKeyValueStorage(
        config.AgentAuthzCommitmentDbType, data_dir, name))
