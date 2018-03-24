from indy_node.server.plugin.agent_authz.cache import AgentAuthzCommitmentCache
from indy_node.server.plugin.agent_authz.commitment_db import CommitmentDb
from indy_node.server.plugin.agent_authz.constants import ACCUMULATOR_1
from indy_node.server.plugin.agent_authz.dynamic_accumulator import \
    DynamicAccumulator
from plenum.persistence.storage import initKeyValueStorage


def get_authz_commitment_cache(data_dir, name, config):
    return AgentAuthzCommitmentCache(initKeyValueStorage(
        config.AgentAuthzCommitmentDbType, data_dir, name))


def get_commitment_db_accum(data_dir, name, config):
    return CommitmentDb(initKeyValueStorage(
        config.AgentAuthzAccumCommDbType, data_dir, name))


def get_dyn_accum(data_dir, name, config):
    return DynamicAccumulator(config.AuthzAccumGenerator[ACCUMULATOR_1],
                              config.AuthzAccumMod[ACCUMULATOR_1],
                              initKeyValueStorage(config.AgentAuthzDynAccumDbType, data_dir, name))
