import pytest

from indy_common.constants import REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, \
    TAG
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import encode_state_value
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="function")
def revoc_reg_def_handler(db_manager):
    f = FakeSomething()
    f.validate = lambda request, action_list: True
    return RevocRegDefHandler(db_manager, f)


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
    with pytest.raises(InvalidClientRequest,
                       match="Format of {} field is not acceptable. "
                             "Expected: 'did:marker:signature_type:schema_ref' or "
                             "'did:marker:signature_type:schema_ref:tag'".format(CRED_DEF_ID)):
        revoc_reg_def_handler.static_validation(revoc_reg_def_request)


def test_revoc_reg_def_dynamic_validation_fails_no_cred_def(revoc_reg_def_handler,
                                                            revoc_reg_def_request):
    operation = revoc_reg_def_request.operation
    cred_def_id = operation.get(CRED_DEF_ID)
    revoc_def_type = operation.get(REVOC_TYPE)
    revoc_def_tag = operation.get(TAG)
    assert cred_def_id
    assert revoc_def_tag
    assert revoc_def_type
    revoc_def_id = RevocRegDefHandler.make_state_path_for_revoc_def(revoc_reg_def_request.identifier,
                                                                    cred_def_id, revoc_def_type,
                                                                    revoc_def_tag)
    revoc_reg_def_handler.state.set(revoc_def_id, "{}")
    with pytest.raises(InvalidClientRequest,
                       match="There is no any CRED_DEF by path"):
        revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)


def test_revoc_reg_def_dynamic_validation_passes(revoc_reg_def_handler,
                                                 revoc_reg_def_request):
    cred_def_id = revoc_reg_def_request.operation.get(CRED_DEF_ID)
    revoc_reg_def_handler.state.set(cred_def_id,
                                    encode_state_value("value", "seqNo", "txnTime"))
    revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)
