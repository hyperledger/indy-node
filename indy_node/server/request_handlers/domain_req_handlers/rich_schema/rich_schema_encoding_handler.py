from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA_ENCODING, RS_ENC_INPUT, RS_ENC_OUTPUT, RS_ENC_ALGORITHM, RS_ENC_TEST_VECS, \
    RS_ENC_ID, RS_ENC_TYPE, RS_ENC_ALG_DESC, RS_ENC_ALG_DOC, RS_ENC_ALG_IMPL, RS_CONTENT

from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from plenum.common.exceptions import InvalidClientRequest

from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class RichSchemaEncodingHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(RICH_SCHEMA_ENCODING, database_manager, write_req_validator)

    def is_json_ld_content(self):
        return False

    def do_static_validation_content(self, content_as_dict, request):
        # 1. check for top level fields
        missing_fields = []
        for field in [RS_ENC_INPUT, RS_ENC_OUTPUT, RS_ENC_ALGORITHM, RS_ENC_TEST_VECS]:
            if not content_as_dict.get(field):
                missing_fields.append("'{}'".format(field))
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set in '{}'".format(missing_fields_str, RS_CONTENT))

        # 2. check for input-output fields
        for io_field in [RS_ENC_INPUT, RS_ENC_OUTPUT]:
            missing_io_fields = []
            for field in [RS_ENC_ID, RS_ENC_TYPE]:
                if not content_as_dict[io_field].get(field):
                    missing_io_fields.append("'{}'".format(field))
            if missing_io_fields:
                missing_io_fields_str = " and ".join(missing_io_fields)
                raise InvalidClientRequest(request.identifier, request.reqId,
                                           "{} must be set in '{}'".format(missing_io_fields_str, io_field))

        # 3. check for algorithm fields
        missing_alg_fields = []
        for field in [RS_ENC_ALG_DESC, RS_ENC_ALG_DOC, RS_ENC_ALG_IMPL]:
            if not content_as_dict[RS_ENC_ALGORITHM].get(field):
                missing_alg_fields.append("'{}'".format(field))
        if missing_alg_fields:
            missing_alg_fields_str = ", ".join(missing_alg_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set in '{}'".format(missing_alg_fields_str, RS_ENC_ALGORITHM))

    def do_dynamic_validation_content(self, request):
        pass
