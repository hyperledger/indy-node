import pytest
from indy_common.auth import Authoriser

from indy_common.constants import NYM, ROLE

from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from ledger.util import F
from plenum.common.constants import STEWARD, TARGET_NYM, IDENTIFIER, VERKEY
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import nym_to_state_key


@pytest.fixture(scope="module")
def nym_handler(db_manager, tconf, write_auth_req_validator):
    return NymHandler(tconf, db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def nym_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={'type': NYM,
                              'dest': randomString(),
                              'role': None,
                              'verkey': randomString()})


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier


def test_nym_static_validation_passes(nym_request, nym_handler: NymHandler):
    nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_without_dest(nym_request, nym_handler: NymHandler):
    del nym_request.operation['dest']
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_none_dest(nym_request, nym_handler: NymHandler):
    nym_request.operation['dest'] = None
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_empty_dest(nym_request, nym_handler: NymHandler):
    nym_request.operation['dest'] = ''
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_spaced_dest(nym_request, nym_handler: NymHandler):
    nym_request.operation['dest'] = ' ' * 5
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_authorized(nym_request, nym_handler: NymHandler):
    for role in Authoriser.ValidRoles:
        nym_request.operation['role'] = role
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_not_authorized_random(nym_request, nym_handler: NymHandler):
    nym_request.operation['role'] = randomString()
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_dynamic_validation_for_new_nym(nym_request, nym_handler: NymHandler, creator):
    nym_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request, 0)

    nym_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request, 0)


def test_nym_dynamic_validation_for_existing_nym(nym_request: Request, nym_handler: NymHandler, creator):
    add_to_idr(nym_handler.database_manager.idr_cache, nym_request.operation['dest'], None)
    nym_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request, 0)

    nym_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request, 0)


def test_update_state(nym_request: Request, nym_handler: NymHandler):
    seq_no = 1
    txn_time = 1560241033
    nym = nym_request.operation.get(TARGET_NYM)
    txn = reqToTxn(nym_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path = nym_to_state_key(nym)

    result = nym_handler.update_state(txn, None, nym_request)
    state_value = nym_handler.get_from_state(path)
    assert state_value == result
    assert state_value[IDENTIFIER] == nym_request.identifier
    assert state_value[F.seqNo.name] == seq_no
    assert state_value[ROLE] == nym_request.operation.get(ROLE)
    assert state_value[VERKEY] == nym_request.operation.get(VERKEY)
