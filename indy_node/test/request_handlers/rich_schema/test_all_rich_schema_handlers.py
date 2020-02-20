import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_ID, RS_TYPE, RS_NAME, RS_VERSION, RS_CONTENT, ENDORSER
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_cred_def_handler import \
    RichSchemaCredDefHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import context_request, make_rich_schema_object_exist
from plenum.common.constants import OP_VER, TRUSTEE
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import SortedDict


def test_update_state(handler_and_request):
    handler, request = handler_and_request
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    op = request.operation

    handler.update_state(txn, None, context_request)

    value = {
        'id': op[RS_ID],
        'rsType': op[RS_TYPE],
        'rsName': op[RS_NAME],
        'rsVersion': op[RS_VERSION],
        'content': op[RS_CONTENT],
        'from': request.identifier,
        'endorser': request.endorser,
        'ver': op[OP_VER],
    }
    primary_key = op[RS_ID]
    secondary_key = "{RS_TYPE}:{RS_NAME}:{RS_VERSION}".format(RS_TYPE=op['rsType'],
                                                              RS_NAME=op['rsName'],
                                                              RS_VERSION=op['rsVersion']).encode()

    value_from_state = handler.get_from_state(primary_key)
    assert SortedDict(value_from_state[0]) == SortedDict(value)
    assert value_from_state[1] == seq_no
    assert value_from_state[2] == txn_time
    assert handler.state.get(secondary_key, isCommitted=False) == op[RS_ID].encode()


def test_dynamic_validation_for_existing(handler_and_request):
    handler, request = handler_and_request
    make_rich_schema_object_exist(handler, request)
    add_to_idr(handler.database_manager.idr_cache, request.identifier, TRUSTEE)
    add_to_idr(handler.database_manager.idr_cache, request.endorser, ENDORSER)
    if isinstance(handler, RichSchemaCredDefHandler):
        handler.dynamic_validation(request, 0)
    else:
        with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
            handler.dynamic_validation(request, 0)


def test_dynamic_validation_for_existing(handler_and_request):
    handler, request = handler_and_request
    make_rich_schema_object_exist(handler, request)
    add_to_idr(handler.database_manager.idr_cache, request.identifier, TRUSTEE)
    add_to_idr(handler.database_manager.idr_cache, request.endorser, ENDORSER)
    if isinstance(handler, RichSchemaCredDefHandler):
        handler.dynamic_validation(request, 0)
    else:
        with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
            handler.dynamic_validation(request, 0)

def test_dynamic_validation_failed_not_authorised(handler_and_request):
    handler, request = handler_and_request
    add_to_idr(handler.database_manager.idr_cache, request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        handler.dynamic_validation(request, 0)


def test_schema_dynamic_validation_passes(handler_and_request):
    handler, request = handler_and_request
    add_to_idr(handler.database_manager.idr_cache, request.identifier, TRUSTEE)
    add_to_idr(handler.database_manager.idr_cache, request.endorser, ENDORSER)
    handler.dynamic_validation(request, 0)
