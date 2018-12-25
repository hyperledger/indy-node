import pytest
from indy_common.constants import ATTRIB

from indy_node.server.request_handlers.domain_req_handlers.attribute_handler import AttributeHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import ENC
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString

from indy_node.test.attrib_txn.test_nym_attrib import attributeData, attributeName, attributeValue


@pytest.fixture(scope="module")
def attrib_handler(db_manager):
    return AttributeHandler(db_manager)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    return identifier


@pytest.fixture(scope="function")
def attrib_request(creator, attributeData):
    return Request(identifier=creator,
                   reqId=5,
                   operation={'type': ATTRIB,
                              'dest': randomString(),
                              'raw': attributeData})


def test_attrib_static_validation_passes(attrib_request, attrib_handler: AttributeHandler):
    attrib_handler.static_validation(attrib_request)


def test_attrib_static_validation_fails(attrib_request, attrib_handler: AttributeHandler):
    attrib_request.operation[ENC] = randomString()
    with pytest.raises(InvalidClientRequest):
        attrib_handler.static_validation(attrib_request)


def test_attrib_dynamic_validation_fails(attrib_request, attrib_handler: AttributeHandler):
    with pytest.raises(InvalidClientRequest):
        attrib_handler.dynamic_validation(attrib_request)


def test_attrib_dynamic_validation_fails_not_owner(attrib_request, attrib_handler: AttributeHandler):
    add_to_idr(attrib_handler.database_manager.idr_cache, attrib_request.operation['dest'], None)
    with pytest.raises(UnauthorizedClientRequest):
        attrib_handler.dynamic_validation(attrib_request)


def test_attrib_dynamic_validation_passes(attrib_request, attrib_handler: AttributeHandler):
    add_to_idr(attrib_handler.database_manager.idr_cache, attrib_request.operation['dest'], None)
    attrib_request._identifier = attrib_request.operation['dest']
    attrib_handler.dynamic_validation(attrib_request)
