import pytest

from indy_common.constants import RS_CONTEXT_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, \
    RS_SCHEMA_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, RS_PRES_DEF_TYPE_VALUE
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
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_pres_def_handler import \
    RichSchemaPresDefHandler
from indy_node.test.helper import rich_schemas_enabled_scope
from indy_node.test.request_handlers.rich_schema.helper import context_request, rich_schema_request, \
    rich_schema_encoding_request, rich_schema_mapping_request, rich_schema_cred_def_request, \
    rich_schema_pres_def_request


@pytest.fixture(scope="module")
def tconf(tconf):
    with rich_schemas_enabled_scope(tconf):
        yield tconf


@pytest.fixture(params=[RS_CONTEXT_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE,
                        RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE,
                        RS_CRED_DEF_TYPE_VALUE, RS_PRES_DEF_TYPE_VALUE])
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
    if request.param == RS_PRES_DEF_TYPE_VALUE:
        return RichSchemaPresDefHandler(db_manager, write_auth_req_validator), rich_schema_pres_def_request()