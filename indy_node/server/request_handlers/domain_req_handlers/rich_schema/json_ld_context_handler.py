from re import findall

from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import JSON_LD_CONTEXT, RS_CONTENT, JSON_LD_CONTEXT_FIELD
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager

URI_REGEX = r'^(?P<scheme>\w+):(?:(?:(?P<url>//[.\w]+)(?:(/(?P<path>[/\w]+)?)?))|(?:(?P<method>\w+):(?P<id>\w+)))'


class JsonLdContextHandler(AbstractRichSchemaObjectHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(JSON_LD_CONTEXT, database_manager, write_req_validator)

    def is_json_ld_content(self):
        return False

    def do_static_validation_content(self, content_as_dict, request: Request):
        if JSON_LD_CONTEXT_FIELD not in content_as_dict:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "'{}' must contain a {} field".format(RS_CONTENT, JSON_LD_CONTEXT_FIELD))

        self._validate_context(content_as_dict[JSON_LD_CONTEXT_FIELD], request.identifier, request.reqId)

    def do_dynamic_validation_content(self, request):
        pass

    def _validate_context(self, context, id, reqId):
        if isinstance(context, list):
            for ctx in context:
                if not isinstance(ctx, dict):
                    if self._bad_uri(ctx):
                        raise InvalidClientRequest(id, reqId, '@context URI {} badly formed'.format(ctx))
        elif isinstance(context, dict):
            pass
        elif isinstance(context, str):
            if self._bad_uri(context):
                raise InvalidClientRequest(id, reqId, '@context URI {} badly formed'.format(context))
        else:
            raise InvalidClientRequest(id, reqId, "'@context' value must be url, array, or object")

    def _bad_uri(self, uri_string):
        url = findall(URI_REGEX, uri_string)
        if not url:
            return True
        return False
