from indy_node.server.plugin.agent_authz.cache import AgentAuthzCommitmentCache
from indy_node.server.plugin.agent_authz.commitment_db import CommitmentDb
from plenum.persistence.storage import initKeyValueStorage


def get_authz_commitment_cache(data_dir, name, config):
    return AgentAuthzCommitmentCache(initKeyValueStorage(
        config.AgentAuthzCommitmentDbType, data_dir, name))


def get_commitment_db_accum(data_dir, name, config):
    return CommitmentDb(initKeyValueStorage(
        config.AgentAuthzAccumCommDbType, data_dir, name))
