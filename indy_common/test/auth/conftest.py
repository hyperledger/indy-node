import pytest
import time

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_map import auth_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.node import Node
from plenum.common.constants import STEWARD, TRUSTEE

from indy_common.constants import ENDORSER, LOCAL_AUTH_POLICY, NETWORK_MONITOR, CONFIG_LEDGER_AUTH_POLICY
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.test.helper import randomOperation
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory

OTHER_ROLE = "OtherRole"
OTHER_IDENTIFIER = "some_other_identifier"

IDENTIFIERS = {TRUSTEE: ["trustee_identifier", "trustee_identifier2", "trustee_identifier3", "trustee_identifier4"],
               STEWARD: ["steward_identifier", "steward_identifier2", "steward_identifier3", "steward_identifier4"],
               ENDORSER: ["endorser_identifier", "endorser_identifier2", "endorser_identifier3",
                          "endorser_identifier4"],
               NETWORK_MONITOR: ["network_monitor_identifier"],
               None: ["identity_owner_identifier", "identity_owner_identifier2", "identity_owner_identifier3",
                      "identity_owner_identifier4"],
               OTHER_ROLE: [OTHER_IDENTIFIER, "some_other_identifier2", "some_other_identifier3",
                            "some_other_identifier4"]}


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


@pytest.fixture(scope="module")
def config_state(constraint_serializer):
    state = PruningState(KeyValueStorageInMemory())
    Node.add_auth_rules_to_config_state(state=state,
                                        auth_map=auth_map,
                                        serializer=constraint_serializer)
    return state


@pytest.fixture(scope='module', params=[v[0] for v in IDENTIFIERS.values()])
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
