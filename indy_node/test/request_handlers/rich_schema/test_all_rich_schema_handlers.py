import pytest

from indy_common.constants import RS_CONTEXT_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, \
    RS_SCHEMA_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, RS_ID, RS_TYPE, RS_NAME, RS_VERSION, RS_CONTENT
from indy_common.types import Request
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.json_ld_context_handler import \
    JsonLdContextHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_cred_def_handler import \
    RichSchemaCredDefHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.rich_schema.helper import context_request, rich_schema_request, \
    rich_schema_encoding_request, rich_schema_mapping_request, rich_schema_cred_def_request
from plenum.common.constants import OP_VER
from plenum.common.txn_util import reqToTxn, append_txn_metadata


@pytest.fixture(params=[RS_CONTEXT_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE,
                        RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE,
                        RS_CRED_DEF_TYPE_VALUE])
def handler_and_request(request, db_manager, write_auth_req_validator) -> (AbstractRichSchemaObjectHandler, Request):
    if request.param == RS_CONTEXT_TYPE_VALUE:
        return JsonLdContextHandler(db_manager, write_auth_req_validator), context_request()
    if request.param == RS_SCHEMA_TYPE_VALUE:
        return RichSchemaHandler(db_manager, write_auth_req_validator), rich_schema_request()
    if request.param == RS_ENCODING_TYPE_VALUE:
        return RichSchemaEncodingHandler(db_manager, write_auth_req_validator), rich_schema_encoding_request()
    if request.param == RS_MAPPING_TYPE_VALUE:
        return RichSchemaMappingHandler(db_manager, write_auth_req_validator), rich_schema_mapping_request()
    if request.param == RS_CRED_DEF_TYPE_VALUE:
        return RichSchemaCredDefHandler(db_manager, write_auth_req_validator), rich_schema_cred_def_request()


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
        'rsContent': op[RS_CONTENT],
        'from': request.identifier,
        'endorser': request.endorser,
        'ver': op[OP_VER],
    }
    primary_key = op[RS_ID]
    secondary_key = "{RS_TYPE}:{RS_NAME}:{RS_VERSION}".format(RS_TYPE=op['rsType'],
                                                              RS_NAME=op['rsName'],
                                                              RS_VERSION=op['rsVersion']).encode()

    assert handler.get_from_state(primary_key) == (value, seq_no, txn_time)
    assert handler.get_from_state(secondary_key) == op[RS_ID]


def make_context_exist(context_request, context_handler):
    identifier, req_id, operation = get_request_data(context_request)
    context_name = get_write_context_name(context_request)
    context_version = get_write_context_version(context_request)
    path = ContextHandler.make_state_path_for_context(identifier, context_name, context_version)
    context_handler.state.set(path, encode_state_value("value", "seqNo", "txnTime"))


def test_context_dynamic_validation_failed_existing_context(context_request, context_handler):
    make_context_exist(context_request, context_handler)
    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        context_handler.dynamic_validation(context_request, 0)


def test_context_dynamic_validation_failed_not_authorised(context_request, context_handler):
    add_to_idr(context_handler.database_manager.idr_cache, context_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        context_handler.dynamic_validation(context_request, 0)


def test_schema_dynamic_validation_passes(context_request, context_handler):
    add_to_idr(context_handler.database_manager.idr_cache, context_request.identifier, TRUSTEE)
    context_handler.dynamic_validation(context_request, 0)