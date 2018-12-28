import pytest

from indy_common.constants import REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, \
    TAG
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="function")
def revoc_reg_def_handler(db_manager):
    def lookup(cred_def_id, is_committed, with_proof):
        return True, None, None, None

    get_handler = FakeSomething()
    get_handler.lookup = lookup
    return RevocRegDefHandler(db_manager, get_handler)


@pytest.fixture(scope="function")
def revoc_reg_def_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   operation={'type': REVOC_REG_DEF,
                              CRED_DEF_ID: 'sample:' * 4,
                              REVOC_TYPE: randomString(),
                              TAG: randomString()
                              })


def test_revoc_reg_def_dynamic_validation_fails_wrong_id(revoc_reg_def_handler,
                                                         revoc_reg_def_request):
    revoc_reg_def_request.operation[CRED_DEF_ID] = 'sample' * 3
    with pytest.raises(InvalidClientRequest):
        revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)


def test_revoc_reg_def_dynamic_validation_fails_no_cred_def(revoc_reg_def_handler,
                                                            revoc_reg_def_request):
    def lookup(cred_def_id, is_committed, with_proof):
        return None, None, None, None

    revoc_reg_def_handler.get_revoc_reg_def.lookup = lookup
    with pytest.raises(InvalidClientRequest):
        revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)


def test_revoc_reg_def_dynamic_validation_passes(revoc_reg_def_handler,
                                                 revoc_reg_def_request):
    revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)
