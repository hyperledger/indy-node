import pytest
import time

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.node import Node
from plenum.common.constants import STEWARD, TRUSTEE

from indy_common.constants import TRUST_ANCHOR, LOCAL_AUTH_POLICY, NETWORK_MONITOR, CONFIG_LEDGER_AUTH_POLICY
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.test.helper import randomOperation
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory


OTHER_IDENTIFIER = "some_other_identifier"


@pytest.fixture(scope='function', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(scope='function')
def action_add():
    return AuthActionAdd(txn_type='SomeType',
                         field='some_field',
                         value='new_value')


@pytest.fixture(scope='function')
def action_edit():
    return AuthActionEdit(txn_type='SomeType',
                          field='some_field',
                          old_value='old_value',
                          new_value='new_value')


@pytest.fixture(scope='module')
def idr_cache():
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    cache.set("trustee_identifier", 1, int(time.time()), role=TRUSTEE,
              verkey="trustee_identifier_verkey", isCommitted=False)
    cache.set("steward_identifier", 2, int(time.time()), role=STEWARD,
              verkey="steward_identifier_verkey", isCommitted=False)
    cache.set("trust_anchor_identifier", 3, int(time.time()), role=TRUST_ANCHOR,
              verkey="trust_anchor_identifier_verkey", isCommitted=False)
    cache.set("network_monitor_identifier", 4, int(time.time()), role=NETWORK_MONITOR,
              verkey="network_monitor_identifier_verkey", isCommitted=False)
    cache.set(OTHER_IDENTIFIER, 5, int(time.time()), role='OtherRole',
              verkey="other_verkey", isCommitted=False)
    return cache


@pytest.fixture(scope="module")
def constraint_serializer():
    return ConstraintsSerializer(domain_state_serializer)


@pytest.fixture(scope="module")
def config_state(constraint_serializer):
    state = PruningState(KeyValueStorageInMemory())
    Node.add_auth_rules_to_config_state(state=state,
                                        auth_map=auth_map,
                                        serializer=constraint_serializer)
    Node.add_auth_rules_to_config_state(state=state,
                                        auth_map=anyone_can_write_map,
                                        serializer=constraint_serializer)
    return state


@pytest.fixture(scope='module')
def write_auth_req_validator(idr_cache,
                             constraint_serializer,
                             config_state):
    validator = WriteRequestValidator(config=FakeSomething(authPolicy=CONFIG_LEDGER_AUTH_POLICY,
                                                           ANYONE_CAN_WRITE=False),
                                      auth_map=auth_map,
                                      cache=idr_cache,
                                      config_state=config_state,
                                      state_serializer=constraint_serializer,
                                      anyone_can_write_map=anyone_can_write_map)
    return validator


@pytest.fixture(scope='module', params=["trustee_identifier", "steward_identifier",
                                        "trust_anchor_identifier", "network_monitor_identifier",
                                        OTHER_IDENTIFIER])
def identifier(request):
    return request.param


@pytest.fixture(scope='module')
def req(identifier):
    return Request(identifier=identifier,
                   operation=randomOperation(),
                   signature='signature')


@pytest.fixture(scope='module')
def write_request_validation(write_auth_req_validator):
    def wrapped(*args, **kwargs):
        try:
            write_auth_req_validator.validate(*args, **kwargs)
        except UnauthorizedClientRequest:
            return False
        return True
    return wrapped
