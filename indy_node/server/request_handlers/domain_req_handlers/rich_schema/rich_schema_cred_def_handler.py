from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_SIG_TYPE, RS_CRED_DEF_MAPPING, \
    RS_CRED_DEF_SCHEMA, RS_CRED_DEF_PUB_KEY

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
                missing_fields.append(field)

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set".format(missing_fields_str))
