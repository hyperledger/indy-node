from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA

from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler

from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class RichSchemaHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(RICH_SCHEMA, database_manager, write_req_validator)

    def is_json_ld_content(self):
        return True

    def do_static_validation_content(self, content_as_dict, request):
        pass

    def do_dynamic_validation_content(self, request):
        pass
