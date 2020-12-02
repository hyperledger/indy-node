import json

import pytest
from indy_common.constants import ATTRIB
from indy_node.persistence.attribute_store import AttributeStore

from indy_node.server.request_handlers.domain_req_handlers.attribute_handler import AttributeHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import ENC, ATTRIB_LABEL
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import randomString

from indy_node.test.attrib_txn.test_nym_attrib import attributeData, attributeName, attributeValue
from plenum.test.helper import sdk_multisign_request_object, sdk_sign_request_objects
from plenum.test.testing_utils import FakeSomething
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope="module")
def attrib_handler(db_manager, write_auth_req_validator):
    return AttributeHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def attrib_request(attributeData, looper, sdk_wallet_client):
    return Request(identifier=sdk_wallet_client[1],
                   reqId=5,
                   signature="signature",
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
        attrib_handler.dynamic_validation(attrib_request, 0)


def test_attrib_dynamic_validation_fails_not_owner(attrib_request, attrib_handler: AttributeHandler):
    add_to_idr(attrib_handler.database_manager.idr_cache, attrib_request.operation['dest'], None)
    with pytest.raises(UnauthorizedClientRequest):
        attrib_handler.dynamic_validation(attrib_request, 0)


def test_attrib_dynamic_validation_passes(attrib_request, attrib_handler: AttributeHandler):
    add_to_idr(attrib_handler.database_manager.idr_cache, attrib_request.operation['dest'], None)
    attrib_request._identifier = attrib_request.operation['dest']
    attrib_handler.dynamic_validation(attrib_request, 0)


def test_update_state(attrib_handler, attrib_request):
    seq_no = 1
    txn_time = 1560241033
    txn_id = "id"
    txn = reqToTxn(attrib_request)
    append_txn_metadata(txn, seq_no, txn_time, txn_id)
    attr_type, path, value, hashed_value, value_bytes = AttributeHandler.prepare_attr_for_state(txn)

    attrib_handler.update_state(txn, None, attrib_request)
    assert attrib_handler.get_from_state(path) == (hashed_value, seq_no, txn_time)

