import random

import pytest
from indy_common.auth import Authoriser

from indy_common.constants import NYM, CLAIM_DEF, SCHEMA, REF
from indy_node.server.request_handlers.domain_req_handlers.claim_def_handler import ClaimDefHandler

from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn

from plenum.common.util import randomString


@pytest.fixture(scope="module")
def claim_def_handler(db_manager, tconf):
    return ClaimDefHandler(tconf, db_manager)


@pytest.fixture(scope="module")
def schema_handler(db_manager, tconf):
    return ClaimDefHandler(tconf, db_manager)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.get_store('idr')
    add_to_idr(idr, identifier, None)
    return identifier


@pytest.fixture(scope="function")
def claim_def_request(creator, schema_request):
    return Request(identifier=creator,
                   reqId=5,
                   operation={'type': CLAIM_DEF,
                              'ref': randomString(),
                              'verkey': randomString()})


@pytest.fixture(scope="function")
def schema_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={'type': SCHEMA,
                              'verkey': randomString()})


def add_to_idr(idr, identifier, role):
    random_s = randomString()
    idr.set(identifier,
            seqNo=5,
            txnTime=random.randint(10, 100000),
            ta=random_s,
            role=role,
            verkey=random_s,
            isCommitted=True)


def test_claim_def_dynamic_validation_for_new_claim_def(claim_def_request, schema_request,
                                                        claim_def_handler: ClaimDefHandler,
                                                        creator, schema_handler):
    schema_handler.updateState(reqToTxn(schema_request))
    claim_def_handler.dynamic_validation(claim_def_request)


def test_claim_def_dynamic_validation_without_schema(claim_def_request, schema_request,
                                                     claim_def_handler: ClaimDefHandler, creator):
    with pytest.raises(InvalidClientRequest) as e:
        claim_def_handler.dynamic_validation(claim_def_request)
    assert "Mentioned seqNo ({}) doesn't exist.".format(claim_def_request.operation[REF]) \
           in e._excinfo[1].args[0]
