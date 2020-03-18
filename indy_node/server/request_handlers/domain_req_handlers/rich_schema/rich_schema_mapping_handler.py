from common.serializers.json_serializer import JsonSerializer
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA_MAPPING, RS_MAPPING_SCHEMA, RS_CONTENT, RS_TYPE, RS_SCHEMA_TYPE_VALUE

from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from plenum.common.exceptions import InvalidClientRequest

from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class RichSchemaMappingHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(RICH_SCHEMA_MAPPING, database_manager, write_req_validator)

    def is_json_ld_content(self):
        return True

    def do_static_validation_content(self, content_as_dict, request):
        if not content_as_dict.get(RS_MAPPING_SCHEMA):
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set in {}".format(RS_MAPPING_SCHEMA, RS_CONTENT))

    def do_dynamic_validation_content(self, request):
        # it has been checked on static validation step that the content is a valid JSON.
        # and it has a schema fields
        content_as_dict = JsonSerializer.loads(request.operation[RS_CONTENT])

        # 1. check that the schema field points to an existing object on the ledger
        schema_id = content_as_dict[RS_MAPPING_SCHEMA]
        schema, _, _ = self.get_from_state(schema_id)
        if not schema:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       'Can not find a schema with id={}; please make sure that it has been added to the ledger'.format(
                                           schema_id))

        # 2. check that the schema field points to an object of the Schema type
        if schema.get(RS_TYPE) != RS_SCHEMA_TYPE_VALUE:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "'{}' field must reference a schema with {}={}".format(
                                           RS_MAPPING_SCHEMA, RS_TYPE, RS_SCHEMA_TYPE_VALUE))
