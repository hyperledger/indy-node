from common.serializers.json_serializer import JsonSerializer
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_SIG_TYPE, RS_CRED_DEF_MAPPING, \
    RS_CRED_DEF_SCHEMA, RS_CRED_DEF_PUB_KEY, RS_CONTENT, RS_TYPE, RS_SCHEMA_TYPE_VALUE, RS_MAPPING_TYPE_VALUE

from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from plenum.common.exceptions import InvalidClientRequest

from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class RichSchemaCredDefHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(RICH_SCHEMA_CRED_DEF, database_manager, write_req_validator)

    def is_json_ld_content(self):
        return False

    def do_static_validation_content(self, content_as_dict, request):
        missing_fields = []
        for field in [RS_CRED_DEF_SIG_TYPE, RS_CRED_DEF_MAPPING, RS_CRED_DEF_SCHEMA, RS_CRED_DEF_PUB_KEY]:
            if not content_as_dict.get(field):
                missing_fields.append("'{}'".format(field))

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set in '{}'".format(missing_fields_str, RS_CONTENT))

    def do_dynamic_validation_content(self, request):
        # it has been checked on static validation step that the content is a valid JSON.
        # and it has schema and mapping fields
        content_as_dict = JsonSerializer.loads(request.operation[RS_CONTENT])
        schema_id = content_as_dict[RS_CRED_DEF_SCHEMA]
        mapping_id = content_as_dict[RS_CRED_DEF_MAPPING]

        # 1. check that the schema field points to an existing object on the ledger
        schema, _, _ = self.get_from_state(schema_id)
        if not schema:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Can not find a referenced '{}' with id={}; please make sure that it has been added to the ledger".format(
                                           RS_CRED_DEF_SCHEMA, schema_id))

        # 2. check that the mapping field points to an existing object on the ledger
        mapping, _, _ = self.get_from_state(mapping_id)
        if not mapping:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Can not find a referenced '{}' with id={}; please make sure that it has been added to the ledger".format(
                                           RS_CRED_DEF_MAPPING, mapping_id))

        # 3. check that the schema field points to an object of the Schema type
        if schema.get(RS_TYPE) != RS_SCHEMA_TYPE_VALUE:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "'{}' field must reference a schema with {}={}".format(
                                           RS_CRED_DEF_SCHEMA, RS_TYPE, RS_SCHEMA_TYPE_VALUE))

        # 4. check that the mapping fields points to an object of the Mapping type
        if mapping.get(RS_TYPE) != RS_MAPPING_TYPE_VALUE:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "'{}' field must reference a mapping with {}={}".format(
                                           RS_CRED_DEF_MAPPING, RS_TYPE, RS_MAPPING_TYPE_VALUE))
