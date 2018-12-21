import random

import pytest
from indy_common.auth import Authoriser

from indy_common.constants import NYM

from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request

from plenum.common.util import randomString


@pytest.fixture(scope="module")
def nym_handler(db_manager):
    return NymHandler(None, db_manager)


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
    idr = db_manager.get_store('idr')
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
    for role in Authoriser.ValidRoles:
        nym_request.operation['role'] = role
        with pytest.raises(UnauthorizedClientRequest):
            nym_handler.dynamic_validation(nym_request)
    add_to_idr(nym_handler.idrCache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request)


def test_nym_dynamic_validation_for_existing_nym(nym_request: Request, nym_handler: NymHandler, creator):
    add_to_idr(nym_handler.idrCache, nym_request.operation['dest'], None)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request)
    nym_request._identifier = nym_request.operation['dest']
    nym_handler.dynamic_validation(nym_request)
