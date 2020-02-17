from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SET_RICH_SCHEMA, JSON_LD_ID, RS_CONTENT, JSON_LD_TYPE

from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from plenum.common.exceptions import InvalidClientRequest

from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class RichSchemaHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(SET_RICH_SCHEMA, database_manager, write_req_validator)

    def do_static_validation_content(self, content_as_dict, request):
        if JSON_LD_ID not in content_as_dict:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "Rich Schema must be a JSON-LD object and contain '{}' field in '{}'".format(
                                           JSON_LD_ID, RS_CONTENT))
        if JSON_LD_TYPE not in content_as_dict:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "Rich Schema must be a JSON-LD object and contain '{}' field in '{}'".format(
                                           JSON_LD_ID, RS_CONTENT))
