import pytest
from indy_common.auth import Authoriser

from indy_common.constants import NYM

from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from plenum.common.constants import STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def nym_handler(db_manager):
    f = FakeSomething()
    f.validate = lambda request, action_list: True
    return NymHandler(db_manager, f)


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
    nym_handler.write_request_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request)

    nym_handler.write_request_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request)


def test_nym_dynamic_validation_for_existing_nym(nym_request: Request, nym_handler: NymHandler, creator):
    add_to_idr(nym_handler.database_manager.idr_cache, nym_request.operation['dest'], None)
    nym_handler.write_request_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request)

    nym_handler.write_request_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request)
