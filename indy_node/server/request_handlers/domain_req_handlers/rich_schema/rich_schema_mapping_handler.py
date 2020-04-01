from common.serializers.json_serializer import JsonSerializer
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import RICH_SCHEMA_MAPPING, RS_MAPPING_SCHEMA, RS_CONTENT, RS_TYPE, RS_SCHEMA_TYPE_VALUE, \
    RS_MAPPING_ENC, RS_MAPPING_RANK, RS_ENCODING_TYPE_VALUE, RS_MAPPING_ATTRIBUTES, RS_MAPPING_ISSUER, \
    RS_MAPPING_ISSUANCE_DATE

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
        # 1. check for missing `schema` or `attributes` fields
        missing_fields = []
        for field in [RS_MAPPING_SCHEMA, RS_MAPPING_ATTRIBUTES]:
            if not content_as_dict.get(field):
                missing_fields.append("'{}'".format(field))

        if missing_fields:
            missing_fields_str = " and ".join(missing_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be set in '{}'".format(missing_fields_str, RS_CONTENT))

        # 2. check for missing defaukt attributes in `attributes` (`issuer` and `issuanceDate`)
        missing_fields = []
        for field in [RS_MAPPING_ISSUER, RS_MAPPING_ISSUANCE_DATE]:
            if not content_as_dict[RS_MAPPING_ATTRIBUTES].get(field):
                missing_fields.append("'{}'".format(field))

        if missing_fields:
            missing_fields_str = " and ".join(missing_fields)
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "{} must be in {}'s '{}'".format(missing_fields_str, RS_CONTENT,
                                                                        RS_MAPPING_ATTRIBUTES))

    def do_dynamic_validation_content(self, request):
        # it has been checked on static validation step that the content is a valid JSON.
        # and it has schema and attributes fields
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

        # 3. find all attribute leaf dicts with encoding-rank pairs
        enc_desc_dicts = list(find_encoding_desc_dicts(content_as_dict[RS_MAPPING_ATTRIBUTES]))

        # 4. check that every dict has encoding and rank fields
        # Note: this check can be done in static validation, but then we will have to traverse the leaf dicts twice
        for desc_dict, attr in enc_desc_dicts:
            if not isinstance(desc_dict, dict):
                raise InvalidClientRequest(request.identifier,
                                           request.reqId,
                                           "{} and {} must be set for the attribute '{}'".format(RS_MAPPING_ENC,
                                                                                                 RS_MAPPING_RANK, attr))

            missing_fields = []
            for field in [RS_MAPPING_ENC, RS_MAPPING_RANK]:
                v = desc_dict.get(field)
                if not v and v != 0:
                    missing_fields.append(field)

            if missing_fields:
                missing_fields_str = " and ".join(missing_fields)
                raise InvalidClientRequest(request.identifier, request.reqId,
                                           "{} must be set for the attribute '{}'".format(missing_fields_str, attr))

        # 5. check that all ranks are unique and form a sequence without gaps
        # Note: this check can be done in static validation, but then we will have to traverse the leaf dicts twice
        expected_ranks = list(range(1, len(enc_desc_dicts) + 1))
        ranks = sorted([desc_dict[RS_MAPPING_RANK] for desc_dict, attr in enc_desc_dicts])
        if ranks != expected_ranks:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "the attribute's ranks are not sequential: expected ranks are all values from 1 to {}".format(
                                           len(enc_desc_dicts)))

        # 6. check that all the enc fields point to an existing object on the ledger of the type Encoding
        for desc_dict, attr in enc_desc_dicts:
            encoding_id = desc_dict[RS_MAPPING_ENC]
            encoding, _, _ = self.get_from_state(encoding_id)
            if not encoding:
                raise InvalidClientRequest(request.identifier,
                                           request.reqId,
                                           "Can not find a referenced '{}' with id={} in the '{}' attribute; please make sure that it has been added to the ledger".format(
                                               RS_MAPPING_ENC, encoding_id, attr))
            if encoding.get(RS_TYPE) != RS_ENCODING_TYPE_VALUE:
                raise InvalidClientRequest(request.identifier,
                                           request.reqId,
                                           "'{}' field in the '{}' attribute must reference an encoding with {}={}".format(
                                               RS_MAPPING_ENC, attr, RS_TYPE, RS_ENCODING_TYPE_VALUE))


def find_encoding_desc_dicts(content, last_attr=None):
    if is_leaf_dict(content):
        yield content, last_attr
        return

    for k, v in content.items():
        if k in []:
            continue
        if isinstance(v, list):
            for item in v:
                for desc_dict, last_attr in find_encoding_desc_dicts(item, k):
                    yield desc_dict, last_attr
        else:
            for desc_dict, last_attr in find_encoding_desc_dicts(v, k):
                yield desc_dict, last_attr


def is_leaf_dict(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, dict):
                return False
            if isinstance(v, list):
                return False
    return True
