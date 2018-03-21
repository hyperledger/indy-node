from hashlib import sha256

import rlp
from rlp.sedes import List, big_endian_int, raw, CountableList
from orderedset import OrderedSet

from indy_node.server.plugin.agent_authz.helper import update_accumulator_val
from plenum.common.constants import VERKEY, NodeHooks, TXN_TYPE
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.types import f

from indy_common.types import Request
from indy_node.server.domain_req_handler import DomainReqHandler
from indy_node.server.plugin.agent_authz.authz_checker import AgentAuthzChecker
from indy_node.server.plugin.agent_authz.cache import AgentAuthzCommitmentCache
from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, \
    GET_AGENT_AUTHZ, GET_AGENT_AUTHZ_ACCUM, ADDRESS, COMMITMENT, AUTHORIZATION, \
    ACCUMULATOR_ID, ACCUMULATOR_1, ACCUMULATOR_2, GET_AGENT_AUTHZ_ACCUM_WIT
from indy_node.server.plugin.agent_authz.exceptions import NoAgentFound
from stp_core.common.log import getlogger

logger = getlogger()


class DomainReqHandlerWithAuthz:
    write_types = {AGENT_AUTHZ, }
    query_types = {GET_AGENT_AUTHZ, GET_AGENT_AUTHZ_ACCUM, GET_AGENT_AUTHZ_ACCUM_WIT}

    POLICY_ADDRESS_STATE_KEY_PREFIX = '\xff'
    ACCUMULATOR_STATE_KEY_PREFIX = '\xfe'
    _state_val_outer_sedes = CountableList(List([raw, big_endian_int, big_endian_int]))

    def __init__(self, domain_state, cache: AgentAuthzCommitmentCache,
                 commitment_db1, commitment_db2, config):
        self.domain_state = domain_state
        self.agent_authz_cache = cache
        self.commitment_dbs = {
            ACCUMULATOR_1: commitment_db1,
            ACCUMULATOR_2: commitment_db2
        }
        self.config = config
        self.commitments = {
            ACCUMULATOR_1: [OrderedSet()],
            ACCUMULATOR_2: [OrderedSet()],
        }

    def _do_static_validation_agent_authz(self, identifier, reqId, operation):
        pass

    def _do_dynamic_validation_agent_authz(self, req: Request):
        try:
            sender_auth, _ = self.agent_authz_cache.get_agent_details(
                policy_address=req.operation[ADDRESS],
                agent_verkey=req.identifier)
            sender = req.identifier
            target = req.operation.get(VERKEY, sender)
            if target != sender:
                try:
                    _, _ = self.agent_authz_cache.get_agent_details(
                        policy_address=req.operation[ADDRESS],
                        agent_verkey=target)
                except NoAgentFound:
                    new_auth = req.operation[AUTHORIZATION]
                    if not AgentAuthzChecker(sender_auth).can_authorize_for(new_auth):
                        raise UnauthorizedClientRequest(
                            req.identifier,
                            req.reqId,
                            '{} cannot authorise {}'.format(sender_auth, new_auth))
                    if AgentAuthzChecker(new_auth).has_prove_auth and COMMITMENT not in req.operation:
                        raise InvalidClientRequest(req.identifier, req.reqId,
                                                   'missed fields - {}'.format(COMMITMENT))
        except NoAgentFound:
            self._validate_policy_creation_req(req)

    def _add_agent_authz(self, txn, isCommitted=False):
        verkey = txn.get(VERKEY, txn[f.IDENTIFIER.nm])
        address = txn[ADDRESS]
        commitment = txn.get(COMMITMENT)
        # Since address and commitment are big numbers
        if isinstance(address, str):
            address = int(address)
        if commitment is not None and isinstance(commitment, str):
            commitment = int(commitment)
        self._update_policy_address(address, verkey,
                                    auth=txn.get(AUTHORIZATION),
                                    commitment=commitment,
                                    is_committed=isCommitted)

    def get_agent_authz(self, request: Request):
        policy_address = request.operation[ADDRESS]
        policy = self.get_policy_from_state(policy_address,
                                            is_committed=True)
        policy = [list(t) for t in policy]
        for item in policy:
            if len(item) > 2 and isinstance(item[2], int):
                item[2] = str(item[2])
        return DomainReqHandler.make_result(request=request,
                                            data=policy,
                                            last_seq_no=0,  # TODO: Fix me
                                            update_time=0,  # TODO: Fix me
                                            proof=None)    # TODO: Fix me

    def get_accum(self, request: Request):
        accum_id = request.operation[ACCUMULATOR_ID]
        accum_value = self.agent_authz_cache.get_accumulator(accum_id,
                                                             is_committed=True)
        accum_value = str(int(accum_value))
        return DomainReqHandler.make_result(request=request,
                                            data=accum_value,
                                            last_seq_no=0,  # TODO: Fix me
                                            update_time=0,  # TODO: Fix me
                                            proof=None)  # TODO: Fix me

    def get_accum_witness(self, request: Request):
        data = []
        accum_id = request.operation[ACCUMULATOR_ID]
        accum_value = self.agent_authz_cache.get_accumulator(accum_id,
                                                             is_committed=True)
        accum_value = str(int(accum_value))
        data.append(accum_value)
        # TODO: Fixme; Too inefficient, store accumulator in commitment db too
        commitment = request.operation[COMMITMENT]
        if isinstance(commitment, int):
            commitment = str(commitment)
        commitment_db = self.commitment_dbs[accum_id]
        if accum_id == ACCUMULATOR_1:
            if commitment_db.has_commitment(commitment):
                commitments = commitment_db.all_commitments_from_index(1)
                old_accum = self.config.AuthzAccumGenerator[accum_id]
                for i, c in enumerate(commitments):
                    if c == commitment:
                        break
                    old_accum = update_accumulator_val(old_accum, int(c),
                                                       self.config.AuthzAccumMod[accum_id])
                data.append(str(old_accum))
                data.append(commitments[i+1:])
        else:
            # The witness for revocation accumulator consists of all members
            # so that `gcd(non_member, product(members))=1`
            data.append(accum_value)    # Redundant
            commitments = commitment_db.all_commitments_from_index(1)
            data.append(commitments)
        return DomainReqHandler.make_result(request=request,
                                            data=data,
                                            last_seq_no=0,  # TODO: Fix me
                                            update_time=0,  # TODO: Fix me
                                            proof=None)  # TODO: Fix me

    def _validate_policy_creation_req(self, req: Request):
        if COMMITMENT not in req.operation:
            raise InvalidClientRequest(req.identifier, req.reqId,
                                       'missed fields - {}'.format(COMMITMENT))
        if VERKEY in req.operation and req.operation[VERKEY] != req.identifier:
            raise InvalidClientRequest(req.identifier, req.reqId,
                                       'either omit {} or make it same '
                                       'as {}'.format(VERKEY, req.identifier))
        if AUTHORIZATION in req.operation and not \
                AgentAuthzChecker(req.operation[AUTHORIZATION]).has_admin_auth:
            raise InvalidClientRequest(
                req.identifier, req.reqId,
                "{} should have the 0'th bit set, found {} instead".
                format(AUTHORIZATION, req.operation[AUTHORIZATION]))

    def _update_policy_address(self, policy_address, agent_verkey,
                               auth=None, commitment=None, is_committed=False):
        # TODO: Fix inefficiency. Check in cache not in state,
        # make Cache support prefix operations
        policy = self.get_policy_from_state(policy_address,
                                            is_committed=is_committed)

        if not policy:
            auth = auth or 1
            commitment = commitment or 0    # TODO: Remove `or 0`
            policy = [[agent_verkey, auth, commitment]]
            self.set_policy_in_state(policy_address, policy)
            self.agent_authz_cache.update_agent_details(policy_address,
                                                        agent_verkey,
                                                        authorisation=auth,
                                                        commitment=commitment,
                                                        is_committed=is_committed)
            self._new_commitment_added(commitment, is_committed=is_committed)
        else:
            commitment = commitment or 0
            updated_policy = self._get_updated_policy(policy, agent_verkey,
                                                      auth, commitment)
            self.set_policy_in_state(policy_address, updated_policy)
            self.agent_authz_cache.update_agent_details(policy_address,
                                                        agent_verkey,
                                                        authorisation=auth,
                                                        commitment=commitment,
                                                        is_committed=is_committed)
            # TODO: Fixme: Not correct always; check for when commitment was
            # already present or PROVE is revoked
            if commitment > 0:
                self._new_commitment_added(commitment, is_committed=is_committed)

    def get_policy_from_state(self, policy_address, is_committed=False):
        return self._get_policy_from_state(self.domain_state, policy_address,
                                           is_committed=is_committed)

    def set_policy_in_state(self, policy_address, policy):
        self.domain_state.set(self.policy_address_to_state_key(policy_address),
                              rlp.encode(policy))

    def _new_commitment_added(self, commitment, is_committed=False):
        self.new_commitment_added(self.domain_state, self.agent_authz_cache,
                                  self.config, commitment,
                                  is_committed=is_committed)
        if not is_committed:
            logger.debug('In _new_commitment_added, adding {} to accumulator {}'
                         .format(commitment, ACCUMULATOR_1))
            self.commitments[ACCUMULATOR_1][-1].add(commitment)

    def _existing_commitment_deleted(self, commitment, is_committed=False):
        self.existing_commitment_deleted(self.domain_state,
                                         self.agent_authz_cache, commitment,
                                         self.config,
                                         is_committed=is_committed)
        if not is_committed:
            self.commitments[ACCUMULATOR_2][-1].add(commitment)

    def on_batch_created(self, batch_idr):
        self.agent_authz_cache.create_batch_from_current(batch_idr)
        self.commitments[ACCUMULATOR_1].append(OrderedSet())
        self.commitments[ACCUMULATOR_2].append(OrderedSet())

    def on_batch_committed(self, state_root):
        self.agent_authz_cache.on_batch_committed(state_root)
        logger.debug(
            '{} adding {} to accumulator {}'.format(self, self.commitments[ACCUMULATOR_1][0], ACCUMULATOR_1))
        for comm in self.commitments[ACCUMULATOR_1][0]:
            self.commitment_dbs[ACCUMULATOR_1].add_commitment(str(comm))

        logger.debug('{} adding {} to accumulator {}'.format(self,
                                                             self.commitments[ACCUMULATOR_2][0],
                                                             ACCUMULATOR_2))
        for comm in self.commitments[ACCUMULATOR_2][0]:
            self.commitment_dbs[ACCUMULATOR_2].add_commitment(str(comm))

        self.commitments[ACCUMULATOR_1] = self.commitments[ACCUMULATOR_1][1:]
        self.commitments[ACCUMULATOR_2] = self.commitments[ACCUMULATOR_2][1:]

    def on_batch_rejected(self):
        self.agent_authz_cache.reject_batch()
        self.commitments[ACCUMULATOR_1] = self.commitments[ACCUMULATOR_1][:-1]
        self.commitments[ACCUMULATOR_2] = self.commitments[ACCUMULATOR_2][:-1]

    @staticmethod
    def new_commitment_added(state, cache, config, commitment, is_committed=False):
        DomainReqHandlerWithAuthz._update_accumulator(state, cache, config,
                                                      ACCUMULATOR_1, commitment,
                                                      is_committed=is_committed)

    @staticmethod
    def existing_commitment_deleted(state, cache, config, commitment,
                                    is_committed=False):
        DomainReqHandlerWithAuthz._update_accumulator(state, cache, config,
                                                      ACCUMULATOR_2, commitment,
                                                      is_committed=is_committed)

    @staticmethod
    def _update_accumulator(state, cache, config, accum_id, value,
                            is_committed=False):
        try:
            accum = cache.get_accumulator(accum_id, is_committed=is_committed)
            accum = int(accum)
        except KeyError:
            accum = config.AuthzAccumGenerator[accum_id]
        updated_val = update_accumulator_val(accum, value, config.AuthzAccumMod[accum_id])
        encoded_val = str(updated_val).encode()
        cache.set_accumulator(ACCUMULATOR_1, encoded_val,
                              is_committed=is_committed)
        state_key = DomainReqHandlerWithAuthz.accum_id_to_state_key(accum_id)
        state.set(state_key, encoded_val)

    @staticmethod
    def _get_policy_from_state(state, policy_address, is_committed=False):
        val = state.get(
            DomainReqHandlerWithAuthz.policy_address_to_state_key(
                policy_address), is_committed)
        return rlp.decode(val,
                          DomainReqHandlerWithAuthz._state_val_outer_sedes) \
            if val is not None else []

    @staticmethod
    def _new_agent_in_state(agent_verkey, auth, commitment):
        return [agent_verkey, auth, commitment]

    @staticmethod
    def _get_updated_policy(existing_policy, agent_verkey, auth, commitment):
        i = 0
        agent_verkey = agent_verkey.encode()
        for (v, a, c) in existing_policy:
            if v == agent_verkey:
                break
            i += 1
        if i == len(existing_policy):
            return (*existing_policy, (agent_verkey, auth, commitment))
        else:
            return (*existing_policy[:i], (agent_verkey, auth, commitment),
                    *existing_policy[(i + 1):])

    @staticmethod
    def policy_address_to_state_key(policy_address: int) -> bytes:
        return '{}:{}'.format(
            DomainReqHandlerWithAuthz.POLICY_ADDRESS_STATE_KEY_PREFIX,
            sha256(str(policy_address).encode()).digest()).encode()

    @staticmethod
    def accum_id_to_state_key(accum_id) -> bytes:
        return '{}:{}'.format(
            DomainReqHandlerWithAuthz.ACCUMULATOR_STATE_KEY_PREFIX,
            sha256(accum_id.encode()).digest()).encode()

    def update_req_handler(self, req_handler):
        req_handler.write_types = req_handler.write_types.union(self.write_types)
        req_handler.query_types = req_handler.query_types.union(self.query_types)

        # TODO: Need a better way for namespacing
        req_handler.agent_authz_cache = self.agent_authz_cache
        req_handler.add_static_validation_handler(AGENT_AUTHZ,
                                                  self._do_static_validation_agent_authz)
        req_handler.add_dynamic_validation_handler(AGENT_AUTHZ,
                                                   self._do_dynamic_validation_agent_authz)
        req_handler.add_state_update_handler(AGENT_AUTHZ, self._add_agent_authz)
        req_handler.add_query_handler(GET_AGENT_AUTHZ, self.get_agent_authz)
        req_handler.add_query_handler(GET_AGENT_AUTHZ_ACCUM, self.get_accum)
        req_handler.add_query_handler(GET_AGENT_AUTHZ_ACCUM_WIT, self.get_accum_witness)
        req_handler.add_post_batch_creation_handler(
            self.on_batch_created)
        req_handler.add_post_batch_commit_handler(
            self.on_batch_committed)
        req_handler.add_post_batch_rejection_handler(
            self.on_batch_rejected)

    @property
    def valid_txn_types(self) -> set:
        return self.write_types.union(self.query_types)

    def pre_send_reply_hook(self, committed_txns, pp_time):
        for txn in committed_txns:
            typ = txn.get(TXN_TYPE)
            if typ in self.valid_txn_types:
                if typ in self.write_types:
                    try:
                        a = self.agent_authz_cache.get_accumulator(ACCUMULATOR_1, True)
                        txn[ACCUMULATOR_1] = int(a)
                    except KeyError:
                        pass
                    try:
                        a = self.agent_authz_cache.get_accumulator(ACCUMULATOR_2, True)
                        txn[ACCUMULATOR_2] = int(a)
                    except KeyError:
                        pass

                self._convert_big_numbers_to_string(txn)

    def _convert_big_numbers_to_string(self, txn):
        # If `ADDRESS`, `COMMITMENT` or ACCUMULATORs are integers, convert them to string
        to_convert = [ADDRESS, COMMITMENT, ACCUMULATOR_1, ACCUMULATOR_2]
        for field in to_convert:
            if isinstance(txn.get(field), int):
                txn[field] = str(txn[field])

    def add_hooks(self, node):
        node.register_hook(NodeHooks.PRE_SEND_REPLY, self.pre_send_reply_hook)
