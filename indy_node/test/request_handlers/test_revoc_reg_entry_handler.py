from functools import partial

import pytest
from indy_node.server.revocation_strategy import IssuedStrategy, RevokedStrategy

from indy_common.constants import SCHEMA, GET_SCHEMA, REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUANCE_BY_DEFAULT, \
    ISSUANCE_ON_DEMAND, VALUE, ISSUANCE_TYPE
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import RevocRegEntryHandler

from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.server.request_handlers.read_req_handlers.get_schema_handler import GetSchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import DOMAIN_LEDGER_ID, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def revoc_reg_entry_handler(db_manager):
    class Validator:
        def __init__(self, state):
            pass

        def validate(self, current_entry, request):
            pass

    revocation_strategy_map = {
        ISSUANCE_BY_DEFAULT: Validator
    }

    def get_current_revoc_entry_and_revoc_def(author_did, revoc_reg_def_id, req_id):
        return True, {VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}}

    f = FakeSomething()
    f.get_current_revoc_entry_and_revoc_def = get_current_revoc_entry_and_revoc_def
    return RevocRegEntryHandler(db_manager, f, revocation_strategy_map)


@pytest.fixture(scope="function")
def revoc_reg_entry_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   operation={'type': REVOC_REG_ENTRY,
                              REVOC_REG_DEF_ID: 'sample'})


def test_revoc_reg_entry_dynamic_validation_passes(revoc_reg_entry_handler,
                                                   revoc_reg_entry_request):
    revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)


def test_revoc_reg_entry_dynamic_validation_fails(revoc_reg_entry_handler,
                                                  revoc_reg_entry_request):
    def validate(self, current_entry, request):
        raise InvalidClientRequest('sample', 'sample')

    revoc_reg_entry_handler.revocation_strategy_map[ISSUANCE_BY_DEFAULT].validate = validate
    with pytest.raises(InvalidClientRequest):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)
