import pytest

from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUANCE_BY_DEFAULT, \
    VALUE, ISSUANCE_TYPE
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import RevocRegEntryHandler

from plenum.common.exceptions import InvalidClientRequest
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

    def get_revocation_strategy(type):
        return Validator

    def get_current_revoc_entry_and_revoc_def(author_did, revoc_reg_def_id, req_id):
        return True, {VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}}

    f = FakeSomething()
    f.get_current_revoc_entry_and_revoc_def = get_current_revoc_entry_and_revoc_def
    return RevocRegEntryHandler(db_manager, f, get_revocation_strategy)


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
    def validate(sample):
        raise InvalidClientRequest('sample', 'sample')

    revoc_reg_entry_handler.get_revocation_strategy = validate
    with pytest.raises(InvalidClientRequest):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)
