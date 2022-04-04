from contextlib import contextmanager
import json
from unittest import mock

from ledger.util import F
from plenum.common.constants import IDENTIFIER, STEWARD, TARGET_NYM, TXN_TYPE, VERKEY
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import append_txn_metadata, reqToTxn
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import nym_to_state_key
import pytest

from indy_common.auth import Authoriser
from indy_common.constants import (
    DIDDOC_CONTENT,
    NYM,
    NYM_VERSION,
    NYM_VERSION_CONVENTION,
    NYM_VERSION_SELF_CERT,
    ROLE,
)
from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception


@pytest.fixture(scope="module")
def nym_handler(db_manager, tconf, write_auth_req_validator):
    return NymHandler(tconf, db_manager, write_auth_req_validator)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier


@pytest.fixture
def doc():
    yield {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://identity.foundation/didcomm-messaging/service-endpoint/v1",
        ],
        "serviceEndpoint": [
            {
                "id": "did:indy:sovrin:123456#didcomm",
                "type": "didcomm-messaging",
                "serviceEndpoint": "https://example.com",
                "recipientKeys": ["#verkey"],
                "routingKeys": [],
            }
        ],
    }


@pytest.fixture
def nym_request_factory(creator, doc):
    def _factory(diddoc_content: dict = None, version: int = None):
        if diddoc_content is None:
            diddoc_content = doc
        return Request(
            identifier=creator,
            reqId=5,
            operation={
                TXN_TYPE: NYM,
                TARGET_NYM: "X3XUxYQM2cfkSMzfMNma73",
                ROLE: None,
                DIDDOC_CONTENT: json.dumps(diddoc_content),
                VERKEY: "HNjfjoeZ7WAHYDSzWcvzyvUABepctabD7QSxopM48fYx",
                **({NYM_VERSION: version} if version is not None else {})
            },
        )

    yield _factory


@pytest.fixture(scope="function")
def nym_request(nym_request_factory):
    yield nym_request_factory()


def test_nym_static_validation_passes(nym_request, nym_handler: NymHandler):
    nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_without_dest(
    nym_request, nym_handler: NymHandler
):
    del nym_request.operation["dest"]
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_none_dest(
    nym_request, nym_handler: NymHandler
):
    nym_request.operation["dest"] = None
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_empty_dest(
    nym_request, nym_handler: NymHandler
):
    nym_request.operation["dest"] = ""
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_failed_with_spaced_dest(
    nym_request, nym_handler: NymHandler
):
    nym_request.operation["dest"] = " " * 5
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_authorized(nym_request, nym_handler: NymHandler):
    for role in Authoriser.ValidRoles:
        nym_request.operation["role"] = role
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_not_authorized_random(
    nym_request, nym_handler: NymHandler
):
    nym_request.operation["role"] = randomString()
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_fails_diddoc_content_with_id(
    nym_request_factory, doc, nym_handler: NymHandler
):
    doc["id"] = randomString()
    nym_request = nym_request_factory(doc)
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_static_validation_diddoc_content_without_context(
    nym_request_factory, doc, nym_handler: NymHandler
):
    del doc["@context"]
    nym_request = nym_request_factory(doc)
    nym_handler.static_validation(nym_request)


def test_nym_static_validation_diddoc_content_fails_with_same_id(
    nym_request_factory, doc, nym_handler: NymHandler
):
    doc["authentication"] = [{
        "id": "did:indy:sovrin:123456#verkey"
    }]
    nym_request = nym_request_factory(doc)
    with pytest.raises(InvalidClientRequest):
        nym_handler.static_validation(nym_request)


def test_nym_dynamic_validation_for_new_nym(
    nym_request, nym_handler: NymHandler, creator
):
    nym_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request, 0)

    nym_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request, 0)


def test_nym_dynamic_validation_for_existing_nym(
    nym_request: Request, nym_handler: NymHandler, creator
):
    add_to_idr(
        nym_handler.database_manager.idr_cache, nym_request.operation["dest"], None
    )
    nym_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)
    nym_handler.dynamic_validation(nym_request, 0)

    nym_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        nym_handler.dynamic_validation(nym_request, 0)


def test_nym_dynamic_validation_for_existing_nym_fails_with_no_changes(
    nym_handler: NymHandler, creator
):
    nym_request = Request(
        identifier=creator, reqId=5, operation={"type": NYM, "dest": randomString()}
    )
    add_to_idr(
        nym_handler.database_manager.idr_cache, nym_request.operation["dest"], None
    )
    add_to_idr(nym_handler.database_manager.idr_cache, creator, STEWARD)

    nym_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(InvalidClientRequest):
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
    assert state_value[DIDDOC_CONTENT] == nym_request.operation.get(DIDDOC_CONTENT)


def test_fail_on_version_update(nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, NYM_VERSION_SELF_CERT)
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)
    nym_data = nym_handler.update_state(txn, None, None, False)
    with pytest.raises(InvalidClientRequest) as e:
        nym_handler._validate_existing_nym(nym_request, nym_request.operation, nym_data)
    e.match("Cannot set version on existing nym")


@pytest.mark.parametrize("version", [-1, 3, 100])
def test_fail_on_bad_version(version: int, nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, version)
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)
    nym_data = nym_handler.update_state(txn, None, None, False)
    with pytest.raises(InvalidClientRequest) as e:
        nym_handler.static_validation(nym_request)
    e.match("Version must be one of")


def test_nym_validation_legacy_convention_x(nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, NYM_VERSION_CONVENTION)
    nym_request.operation[TARGET_NYM] = "NOTDERIVEDFROMVERKEY"
    nym_request.operation[VERKEY] = "HNjfjoeZ7WAHYDSzWcvzyvUABepctabD7QSxopM48fYz"
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)
    with pytest.raises(InvalidClientRequest) as e:
        nym_handler._validate_new_nym(nym_request, nym_request.operation)
    e.match("Identifier with version 1")


def test_nym_validation_legacy_convention(nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, NYM_VERSION_CONVENTION)
    nym_request.operation[TARGET_NYM] = "X3XUxYQM2cfkSMzfMNma73"
    nym_request.operation[VERKEY] = "HNjfjoeZ7WAHYDSzWcvzyvUABepctabD7QSxopM48fYz"
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)

    with mock.patch.object(nym_handler, "write_req_validator"):
        nym_handler._validate_new_nym(nym_request, nym_request.operation)


def test_nym_validation_self_certifying_x(nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, NYM_VERSION_SELF_CERT)
    nym_request.operation[TARGET_NYM] = "NOTSELFCERTIFYING"
    nym_request.operation[VERKEY] = "HNjfjoeZ7WAHYDSzWcvzyvUABepctabD7QSxopM48fYz"
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)
    with pytest.raises(InvalidClientRequest) as e:
        nym_handler._validate_new_nym(nym_request, nym_request.operation)
    e.match("Identifier with version 2")


def test_nym_validation_self_certifying(nym_request: Request, nym_handler: NymHandler, doc, nym_request_factory):
    nym_request = nym_request_factory(doc, NYM_VERSION_SELF_CERT)
    nym_request.operation[TARGET_NYM] = "Dyqasan6xG5KsKdLufxCEf"
    nym_request.operation[VERKEY] = "HNjfjoeZ7WAHYDSzWcvzyvUABepctabD7QSxopM48fYz"
    txn = reqToTxn(nym_request)
    seq_no = 1
    txn_time = 1560241033
    append_txn_metadata(txn, seq_no, txn_time)

    with mock.patch.object(nym_handler, "write_req_validator"):
        nym_handler._validate_new_nym(nym_request, nym_request.operation)
