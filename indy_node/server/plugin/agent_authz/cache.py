from indy_node.server.plugin.agent_authz.authz_checker import AgentAuthzChecker
from indy_node.server.plugin.agent_authz.constants import ACCUMULATOR_1, \
    ACCUMULATOR_2
from indy_node.server.plugin.agent_authz.exceptions import NoAgentFound
from storage.kv_store import KeyValueStorage
from storage.optimistic_kv_store import OptimisticKVStore


class AgentAuthzCommitmentCache(OptimisticKVStore):
    """
    Used to answer 2 questions:
        1. Given​ ​a policy address and an agent key, get the authorisation
        bitset and commitment if any
            eg. <addr><delimiter><verkey>: <authr><delimiter><commitment>
        2. Given​ ​an​ accumulator id (provision-add-only, revocation-add-only
        or both),​ ​return​ its value
    """

    ACCUMULATOR1_ID = ACCUMULATOR_1
    ACCUMULATOR2_ID = ACCUMULATOR_2
    KEY_DELIMITER = ':'
    VALUE_DELIMITER = ':'

    def __init__(self, kv_store: KeyValueStorage):
        super().__init__(kv_store)

    def update_agent_details(self, policy_address, agent_verkey,
                             authorisation=None, commitment=None,
                             is_committed=False):
        if authorisation is None and commitment is None:
            raise ValueError('At least one of authorisation and commitment is '
                             'needed, but both are None')
        key = self.create_cache_key_for_agent(policy_address, agent_verkey)
        if None not in (authorisation, commitment):
            # Updating both authorisation and commitment, so only check
            # that the new authorisation and commitment are compatible
            if self.are_auth_and_commitment_compatible(authorisation, commitment):
                self.set(key, self.create_cache_value_for_agent(authorisation,
                                                                commitment))
            else:
                raise ValueError
        else:
            try:
                existing_auth, existing_commitment = self._get_key_details(
                    key, is_committed=is_committed)
            except KeyError:
                existing_auth, existing_commitment = 0, 0

            if authorisation is None:
                if self.are_auth_and_commitment_compatible(existing_auth,
                                                           commitment):
                    self.set(key,
                             self.create_cache_value_for_agent(existing_auth,
                                                               commitment))
                    return
                else:
                    raise ValueError

            if commitment is None:
                if self.are_auth_and_commitment_compatible(authorisation,
                                                           existing_commitment):
                    self.set(key,
                             self.create_cache_value_for_agent(authorisation,
                                                               existing_commitment))
                elif AgentAuthzChecker(authorisation).has_prove_auth:
                    if existing_commitment > 0:
                        self.set(key,
                                 self.create_cache_value_for_agent(
                                     authorisation, existing_commitment))
                    else:
                        raise ValueError
                else:
                    # Losing `PROVE` authorisation, set commitment to 0
                    self.set(key,
                             self.create_cache_value_for_agent(authorisation, 0))

    def get_agent_details(self, policy_address, agent_verkey, is_committed=False):
        key = self.create_cache_key_for_agent(policy_address, agent_verkey)
        try:
            return self._get_key_details(key, is_committed=is_committed)
        except KeyError:
            raise NoAgentFound(policy_address, agent_verkey)

    def _get_key_details(self, key, is_committed=False):
        existing_details = self.get(key, is_committed=is_committed).decode()
        return tuple(map(int, existing_details.split(self.VALUE_DELIMITER)))

    def set_accumulator(self, accum_id, accum_value, is_committed=False):
        self.validate_accum_id(accum_id)
        self.set(accum_id, accum_value, is_committed=is_committed)

    def get_accumulator(self, accum_id, is_committed=False):
        self.validate_accum_id(accum_id)
        return self.get(accum_id, is_committed=is_committed)

    def on_batch_committed(self, state_root):
        if self.first_batch_idr != state_root:
            raise ValueError('integrity check failed, expected {}, got {}'.format(self.first_batch_idr, state_root))
        self.commit_batch()

    @staticmethod
    def validate_accum_id(accum_id):
        if accum_id not in (AgentAuthzCommitmentCache.ACCUMULATOR1_ID,
                            AgentAuthzCommitmentCache.ACCUMULATOR2_ID):
            raise KeyError('Unknown accumulator id {}'.format(accum_id))

    @staticmethod
    def create_cache_key_for_agent(policy_address, verkey):
        return '{}{}{}'.format(policy_address,
                               AgentAuthzCommitmentCache.KEY_DELIMITER,
                               verkey).encode()

    @staticmethod
    def create_cache_value_for_agent(authorisation, commitment):
        return '{}{}{}'.format(authorisation,
                               AgentAuthzCommitmentCache.VALUE_DELIMITER,
                               commitment).encode()

    @staticmethod
    def are_auth_and_commitment_compatible(authorisation, commitment):
        has_prove_auth = AgentAuthzChecker(authorisation).has_prove_auth
        return has_prove_auth if commitment > 0 else not has_prove_auth
