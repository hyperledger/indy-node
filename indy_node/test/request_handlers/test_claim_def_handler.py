import pytest

from indy_common.constants import NYM, CLAIM_DEF, REF
from indy_node.server.request_handlers.domain_req_handlers.claim_def_handler import ClaimDefHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception

from plenum.common.constants import STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest, UnknownIdentifier
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, get_seq_no

from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def claim_def_handler(db_manager):
    f = FakeSomething()
    f.validate = lambda request, action_list: True
    return ClaimDefHandler(db_manager, f)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, STEWARD)
    return identifier


@pytest.fixture(scope="function")
def claim_def_request(creator, schema_request):
    return Request(identifier=creator,
                   reqId=5,
                   operation={'type': CLAIM_DEF,
                              'ref': schema_request,
                              'verkey': randomString()})


def test_claim_def_dynamic_validation_for_new_claim_def(claim_def_request, schema_request,
                                                        claim_def_handler: ClaimDefHandler):
    schema = reqToTxn(schema_request)
    claim_def_request.operation[REF] = get_seq_no(schema)
    claim_def_handler.ledger.appendTxns([schema])
    claim_def_handler.dynamic_validation(claim_def_request)


def test_claim_def_dynamic_validation_without_permission(claim_def_request, schema_request,
                                                         claim_def_handler: ClaimDefHandler):
    claim_def_handler.write_request_validator.validate = get_exception(True)
    schema = reqToTxn(schema_request)
    claim_def_request.operation[REF] = get_seq_no(schema)
    claim_def_handler.ledger.appendTxns([schema])

    test_identifier = randomString()
    idr = claim_def_handler.database_manager.idr_cache
    add_to_idr(idr, test_identifier, "")

    request = Request(identifier=test_identifier,
                      reqId=claim_def_request.reqId,
                      operation=claim_def_request.operation)
    with pytest.raises(UnauthorizedClientRequest) as e:
        claim_def_handler.dynamic_validation(request)


def test_claim_def_dynamic_validation_for_unknown_identifier(claim_def_request, schema_request,
                                                             claim_def_handler: ClaimDefHandler):
    claim_def_handler.write_request_validator.validate = get_exception(True)
    test_identifier = randomString()
    schema = reqToTxn(schema_request)
    claim_def_request.operation[REF] = get_seq_no(schema)
    claim_def_handler.ledger.appendTxns([schema])
    request = Request(identifier=test_identifier,
                      reqId=claim_def_request.reqId,
                      operation=claim_def_request.operation)
    with pytest.raises(UnauthorizedClientRequest) as e:
        claim_def_handler.dynamic_validation(request)


def test_claim_def_dynamic_validation_without_schema(claim_def_request, schema_request,
                                                     claim_def_handler: ClaimDefHandler):
    with pytest.raises(InvalidClientRequest) as e:
        claim_def_handler.dynamic_validation(claim_def_request)
    assert "Mentioned seqNo ({}) doesn't exist.".format(claim_def_request.operation[REF]) \
           in e._excinfo[1].args[0]


def test_claim_def_dynamic_validation_without_ref_to_not_schema(claim_def_request, schema_request,
                                                                claim_def_handler: ClaimDefHandler, creator):
    nym = reqToTxn(Request(identifier=creator, operation={'type': NYM}))
    claim_def_request.operation[REF] = get_seq_no(nym)
    claim_def_handler.ledger.appendTxns([nym])
    with pytest.raises(InvalidClientRequest) as e:
        claim_def_handler.dynamic_validation(claim_def_request)
    assert "Mentioned seqNo ({}) isn't seqNo of the schema.".format(claim_def_request.operation[REF]) \
           in e._excinfo[1].args[0]
