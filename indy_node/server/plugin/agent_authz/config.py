from plenum.common.constants import KeyValueStorageType


def get_config(config):
    # NOTE: `AuthzAccumMod` has a dummy value, it will not be used and not of
    # the correct size either
    config.AuthzAccumMod = 77   # 7*11 = (2*3+1)*(2*5+1)
    config.AuthzAccumGenerator = 5
    config.AuthzAccumElementMax = 5
    config.AgentAuthzCommitmentDbType = KeyValueStorageType.Leveldb
    config.AgentAuthzCommitmentCacheDbName = 'agent_authz_commitment_cache'
    return config
