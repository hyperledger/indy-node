import pytest

from indy_common.constants import CRED_DEF_ID, REVOC_TYPE, \
    TAG
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.server.request_handlers.utils import encode_state_value


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
    add_to_idr(revoc_reg_def_handler.database_manager.idr_cache,
               revoc_reg_def_request.identifier,
               TRUSTEE)
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
    add_to_idr(revoc_reg_def_handler.database_manager.idr_cache,
               revoc_reg_def_request.identifier,
               TRUSTEE)
    cred_def_id = revoc_reg_def_request.operation.get(CRED_DEF_ID)
    revoc_reg_def_handler.state.set(cred_def_id.encode(),
                                    encode_state_value("value", "seqNo", "txnTime"))
    revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)


def test_revoc_reg_def_dynamic_validation_without_permission(revoc_reg_def_handler,
                                                             revoc_reg_def_request):
    add_to_idr(revoc_reg_def_handler.database_manager.idr_cache,
               revoc_reg_def_request.identifier,
               None)
    cred_def_id = revoc_reg_def_request.operation.get(CRED_DEF_ID)
    revoc_reg_def_handler.state.set(cred_def_id.encode(),
                                    encode_state_value("value", "seqNo", "txnTime"))
    with pytest.raises(UnauthorizedClientRequest,
                       match="Not enough TRUSTEE signatures"):
        revoc_reg_def_handler.dynamic_validation(revoc_reg_def_request)


def test_update_state(revoc_reg_def_handler, revoc_reg_def_request):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(revoc_reg_def_request)
    append_txn_metadata(txn, seq_no, txn_time)
    value = get_payload_data(txn)
    path = RevocRegDefHandler.prepare_revoc_def_for_state(txn,
                                                          path_only=True)

    revoc_reg_def_handler.update_state(txn, None, revoc_reg_def_request)
    assert revoc_reg_def_handler.get_from_state(path) == (value, seq_no, txn_time)
