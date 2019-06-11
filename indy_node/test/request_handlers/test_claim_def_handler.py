import pytest

from indy_common.constants import NYM, CLAIM_DEF, REF
from indy_common.req_utils import get_txn_claim_def_public_keys
from indy_node.server.request_handlers.domain_req_handlers.claim_def_handler import ClaimDefHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception

from plenum.common.constants import STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest, UnknownIdentifier
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, get_seq_no, append_txn_metadata, get_payload_data

from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething
from indy_common.test.auth.conftest import write_auth_req_validator, constraint_serializer, config_state


@pytest.fixture(scope="module")
def claim_def_handler(db_manager, write_auth_req_validator):
    return ClaimDefHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, STEWARD)
    return identifier


@pytest.fixture(scope="function")
def schema(schema_request):
    return reqToTxn(schema_request)


@pytest.fixture(scope="function")
def claim_def_request(creator, schema):
    return Request(identifier=creator,
                   reqId=5,
                   signature="sig",
                   operation={'type': CLAIM_DEF,
                              'ref': get_seq_no(schema),
                              'verkey': randomString()})


def test_claim_def_dynamic_validation_without_schema(claim_def_request,
                                                     claim_def_handler: ClaimDefHandler):
    with pytest.raises(InvalidClientRequest) as e:
        claim_def_handler.dynamic_validation(claim_def_request)
    assert "Mentioned seqNo ({}) doesn't exist.".format(claim_def_request.operation[REF]) \
           in e._excinfo[1].args[0]


def test_claim_def_dynamic_validation_for_new_claim_def(claim_def_request, schema,
                                                        claim_def_handler: ClaimDefHandler):
    claim_def_handler.ledger.appendTxns([schema])
    claim_def_handler.dynamic_validation(claim_def_request)


def test_claim_def_dynamic_validation_without_permission(claim_def_request, schema,
                                                         claim_def_handler: ClaimDefHandler):
    claim_def_handler.ledger.appendTxns([schema])
    test_identifier = randomString()
    idr = claim_def_handler.database_manager.idr_cache
    add_to_idr(idr, test_identifier, "")

    request = Request(identifier=test_identifier,
                      reqId=claim_def_request.reqId,
                      signature="sig",
                      operation=claim_def_request.operation)
    with pytest.raises(UnauthorizedClientRequest,
                       match="Not enough .* signatures"):
        claim_def_handler.dynamic_validation(request)


def test_claim_def_dynamic_validation_for_unknown_identifier(claim_def_request, schema,
                                                             claim_def_handler: ClaimDefHandler):
    test_identifier = randomString()
    claim_def_handler.ledger.appendTxns([schema])
    request = Request(identifier=test_identifier,
                      reqId=claim_def_request.reqId,
                      operation=claim_def_request.operation)
    with pytest.raises(UnauthorizedClientRequest,
                       match='DID {} is not found in the Ledger'.format(test_identifier)):
        claim_def_handler.dynamic_validation(request)


def test_claim_def_dynamic_validation_without_ref_to_not_schema(claim_def_request, schema,
                                                                claim_def_handler: ClaimDefHandler, creator):
    claim_def_handler.ledger.appendTxns([schema])
    nym = reqToTxn(Request(identifier=creator, operation={'type': NYM}))
    claim_def_request.operation[REF] = get_seq_no(nym)
    claim_def_handler.ledger.appendTxns([nym])
    with pytest.raises(InvalidClientRequest) as e:
        claim_def_handler.dynamic_validation(claim_def_request)
    assert "Mentioned seqNo ({}) isn't seqNo of the schema.".format(claim_def_request.operation[REF]) \
           in e._excinfo[1].args[0]


def test_update_state(claim_def_request, claim_def_handler: ClaimDefHandler):
    seq_no = 1
    txn_time = 1560241033
    txn_id = "id"
    txn = reqToTxn(claim_def_request)
    print(get_payload_data(txn))
    print(get_txn_claim_def_public_keys(txn))
    append_txn_metadata(txn, seq_no, txn_time, txn_id)
    path, value_bytes = ClaimDefHandler.prepare_claim_def_for_state(txn)

    claim_def_handler.update_state(txn, None, claim_def_request)
    assert claim_def_handler.get_from_state(path) == (value_bytes, seq_no, txn_time)

