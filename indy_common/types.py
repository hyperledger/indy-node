import json
from copy import deepcopy
from hashlib import sha256

from plenum.common.constants import TARGET_NYM, NONCE, RAW, ENC, HASH, NAME, \
    VERSION, ORIGIN, FORCE
from plenum.common.messages.node_message_factory import node_message_factory

from plenum.common.messages.message_base import MessageValidator
from plenum.common.request import Request as PRequest
from plenum.common.types import OPERATION
from plenum.common.messages.node_messages import NonNegativeNumberField
from plenum.common.messages.fields import ConstantField, IdentifierField, LimitedLengthStringField, TxnSeqNoField, \
    Sha256HexField, JsonField, MapField, BooleanField, VersionField, ChooseField, IntegerField, IterableField, \
    AnyMapField, NonEmptyStringField
from plenum.common.messages.client_request import ClientOperationField as PClientOperationField
from plenum.common.messages.client_request import ClientMessageValidator as PClientMessageValidator
from plenum.common.util import is_network_ip_address_valid, is_network_port_valid
from plenum.config import JSON_FIELD_LIMIT, NAME_FIELD_LIMIT, DATA_FIELD_LIMIT, \
    NONCE_FIELD_LIMIT, ORIGIN_FIELD_LIMIT, \
    ENC_FIELD_LIMIT, RAW_FIELD_LIMIT, SIGNATURE_TYPE_FIELD_LIMIT, \
    HASH_FIELD_LIMIT, VERSION_FIELD_LIMIT

from indy_common.constants import TXN_TYPE, allOpKeys, ATTRIB, GET_ATTR, \
    DATA, GET_NYM, reqOpKeys, GET_TXNS, GET_SCHEMA, GET_CLAIM_DEF, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, CONFIG_LEDGER_ID, POOL_UPGRADE, POOL_CONFIG, \
    DISCLO, ATTR_NAMES, REVOCATION, SCHEMA, ENDPOINT, CLAIM_DEF, REF, SIGNATURE_TYPE, SCHEDULE, SHA256, \
    TIMEOUT, JUSTIFICATION, JUSTIFICATION_MAX_SIZE, REINSTALL, WRITES, PRIMARY, START, CANCEL, \
    REVOC_REG_DEF, ISSUANCE_TYPE, MAX_CRED_NUM, PUBLIC_KEYS, \
    TAILS_HASH, TAILS_LOCATION, ID, TYPE, TAG, CRED_DEF_ID, VALUE, \
    REVOC_REG_ENTRY, ISSUED, REVOC_REG_DEF_ID, REVOKED, ACCUM, PREV_ACCUM, \
    GET_REVOC_REG_DEF


class Request(PRequest):
    def signingState(self, identifier=None):
        """
        Special signing state where the the data for an attribute is hashed
        before signing
        :return: state to be used when signing
        """
        if self.operation.get(TXN_TYPE) == ATTRIB:
            d = deepcopy(super().signingState(identifier=identifier))
            op = d[OPERATION]
            keyName = {RAW, ENC, HASH}.intersection(set(op.keys())).pop()
            op[keyName] = sha256(op[keyName].encode()).hexdigest()
            return d
        return super().signingState(identifier=identifier)


class ClientGetNymOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_NYM)),
        (TARGET_NYM, IdentifierField()),
    )


class ClientDiscloOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(DISCLO)),
        (DATA, LimitedLengthStringField(max_length=DATA_FIELD_LIMIT)),
        (NONCE, LimitedLengthStringField(max_length=NONCE_FIELD_LIMIT)),
        (TARGET_NYM, IdentifierField(optional=True)),
    )


class GetSchemaField(MessageValidator):
    schema = (
        (NAME, LimitedLengthStringField(max_length=NAME_FIELD_LIMIT)),
        (VERSION, VersionField(components_number=(2, 3,), max_length=VERSION_FIELD_LIMIT)),
        (ORIGIN, LimitedLengthStringField(max_length=ORIGIN_FIELD_LIMIT, optional=True)),
    )


class SchemaField(MessageValidator):
    schema = (
        (NAME, LimitedLengthStringField(max_length=NAME_FIELD_LIMIT)),
        (VERSION, VersionField(components_number=(2, 3,), max_length=VERSION_FIELD_LIMIT)),
        (ATTR_NAMES, IterableField(LimitedLengthStringField(max_length=NAME_FIELD_LIMIT))),
    )


class ClaimDefField(MessageValidator):
    schema = (
        (PRIMARY, AnyMapField()),
        (REVOCATION, AnyMapField(optional=True)),
    )


class RevocDefValueField(MessageValidator):
    schema = (
        (ISSUANCE_TYPE, NonEmptyStringField()),
        (MAX_CRED_NUM, IntegerField()),
        (PUBLIC_KEYS, AnyMapField()),
        (TAILS_HASH, NonEmptyStringField()),
        (TAILS_LOCATION, NonEmptyStringField()),
    )


class ClientRevocDefSubmitField(MessageValidator):
    schema = (
        (ID, NonEmptyStringField()),
        (TYPE, NonEmptyStringField()),
        (TAG, NonEmptyStringField()),
        (CRED_DEF_ID, NonEmptyStringField()),
        (VALUE, RevocDefValueField())
    )


class RevocRegEntryValueField(MessageValidator):
    schema = (
        (PREV_ACCUM, NonEmptyStringField()),
        (ACCUM, NonEmptyStringField()),
        (ISSUED, IterableField(inner_field_type=IntegerField())),
        (REVOKED, IterableField(inner_field_type=IntegerField()))
    )


class ClientRevocRegEntrySubmitField(MessageValidator):
    schema = (
        (REVOC_REG_DEF_ID, NonEmptyStringField()),
        (TYPE, NonEmptyStringField()),
        (VALUE, RevocRegEntryValueField())
    )


class ClientSchemaOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(SCHEMA)),
        (DATA, SchemaField()),
    )


class ClientGetSchemaOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_SCHEMA)),
        (TARGET_NYM, IdentifierField()),
        (DATA, GetSchemaField()),
    )


class ClientAttribOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(ATTRIB)),
        (TARGET_NYM, IdentifierField(optional=True)),
        (RAW, JsonField(max_length=JSON_FIELD_LIMIT, optional=True)),
        (ENC, LimitedLengthStringField(max_length=ENC_FIELD_LIMIT, optional=True)),
        (HASH, Sha256HexField(optional=True)),
    )

    def _validate_message(self, msg):
        self._validate_field_set(msg)
        if RAW in msg:
            self.__validate_raw_field(msg[RAW])

    def _validate_field_set(self, msg):
        fields_n = sum(1 for f in (RAW, ENC, HASH) if f in msg)
        if fields_n == 0:
            self._raise_missed_fields(RAW, ENC, HASH)
        if fields_n > 1:
            self._raise_invalid_message(
                "only one field from {}, {}, {} is expected".format(
                    RAW, ENC, HASH)
            )

    def __validate_raw_field(self, raw_field):
        raw = self.__decode_raw_field(raw_field)
        if not isinstance(raw, dict):
            self._raise_invalid_fields(RAW, type(raw),
                                       'should be a dict')
        if len(raw) != 1:
            self._raise_invalid_fields(RAW, raw,
                                       'should contain one attribute')
        if ENDPOINT in raw:
            self.__validate_endpoint_ha_field(raw[ENDPOINT])

    def __decode_raw_field(self, raw_field):
        return json.loads(raw_field)

    def __validate_endpoint_ha_field(self, endpoint):
        if endpoint is None:
            return  # remove the attribute, valid case
        HA_NAME = 'ha'
        ha = endpoint.get(HA_NAME)
        if ha is None:
            return  # remove ha attribute, valid case
        if ':' not in ha:
            self._raise_invalid_fields(ENDPOINT, endpoint,
                                       "invalid endpoint format "
                                       "ip_address:port")
        ip, port = ha.split(':')
        if not is_network_ip_address_valid(ip):
            self._raise_invalid_fields('ha', ha,
                                       'invalid endpoint address')
        if not is_network_port_valid(port):
            self._raise_invalid_fields('ha', ha,
                                       'invalid endpoint port')


class ClientGetAttribOperation(ClientAttribOperation):
    schema = (
        (TXN_TYPE, ConstantField(GET_ATTR)),
        (TARGET_NYM, IdentifierField(optional=True)),
        (RAW, LimitedLengthStringField(max_length=RAW_FIELD_LIMIT, optional=True)),
        (ENC, LimitedLengthStringField(max_length=ENC_FIELD_LIMIT, optional=True)),
        (HASH, Sha256HexField(optional=True)),
    )

    def _validate_message(self, msg):
        self._validate_field_set(msg)


class ClientClaimDefSubmitOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(CLAIM_DEF)),
        (REF, TxnSeqNoField()),
        (DATA, ClaimDefField()),
        (SIGNATURE_TYPE, LimitedLengthStringField(max_length=SIGNATURE_TYPE_FIELD_LIMIT)),
    )


class ClientClaimDefGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_CLAIM_DEF)),
        (REF, TxnSeqNoField()),
        (ORIGIN, IdentifierField()),
        (SIGNATURE_TYPE, LimitedLengthStringField(max_length=SIGNATURE_TYPE_FIELD_LIMIT)),
    )


class ClientGetRevocRegDefField(MessageValidator):
    schema = (
        (ID, NonEmptyStringField()),
        (TYPE, ConstantField(GET_REVOC_REG_DEF)),
    )


class ClientPoolUpgradeOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(POOL_UPGRADE)),
        (ACTION, ChooseField(values=(START, CANCEL,))),
        (VERSION, VersionField(components_number=(2, 3,), max_length=VERSION_FIELD_LIMIT)),
        # TODO replace actual checks (idr, datetime)
        (SCHEDULE, MapField(IdentifierField(),
                            NonEmptyStringField(), optional=True)),
        (SHA256, Sha256HexField()),
        (TIMEOUT, NonNegativeNumberField(optional=True)),
        (JUSTIFICATION, LimitedLengthStringField(max_length=JUSTIFICATION_MAX_SIZE, optional=True, nullable=True)),
        (NAME, LimitedLengthStringField(max_length=NAME_FIELD_LIMIT)),
        (FORCE, BooleanField(optional=True)),
        (REINSTALL, BooleanField(optional=True)),
    )


class ClientPoolConfigOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(POOL_CONFIG)),
        (WRITES, BooleanField()),
        (FORCE, BooleanField(optional=True)),
    )


class ClientOperationField(PClientOperationField):

    _specific_operations = {
        SCHEMA: ClientSchemaOperation(),
        ATTRIB: ClientAttribOperation(),
        GET_ATTR: ClientGetAttribOperation(),
        CLAIM_DEF: ClientClaimDefSubmitOperation(),
        GET_CLAIM_DEF: ClientClaimDefGetOperation(),
        DISCLO: ClientDiscloOperation(),
        GET_NYM: ClientGetNymOperation(),
        GET_SCHEMA: ClientGetSchemaOperation(),
        POOL_UPGRADE: ClientPoolUpgradeOperation(),
        POOL_CONFIG: ClientPoolConfigOperation(),
        REVOC_REG_DEF: ClientRevocDefSubmitField(),
        REVOC_REG_ENTRY: ClientRevocRegEntrySubmitField(),
        GET_REVOC_REG_DEF: ClientGetRevocRegDefField(),
    }

    # TODO: it is a workaround because INDY-338, `operations` must be a class
    # constant
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations.update(self._specific_operations)


class ClientMessageValidator(PClientMessageValidator):

    # extend operation field
    schema = tuple(
        map(lambda x: (x[0], ClientOperationField()) if x[0] == OPERATION else x,
            PClientMessageValidator.schema)
    )


# THE CODE BELOW MIGHT BE NEEDED IN THE FUTURE, THEREFORE KEEPING IT
# class LedgerIdField(PLedgerIdField):
#     ledger_ids = PLedgerIdField.ledger_ids + (CONFIG_LEDGER_ID,)
#
#
# class LedgerInfoField(PLedgerInfoField):
#     _ledger_id_class = LedgerIdField


# TODO: it is a workaround which helps extend some fields from
# downstream projects, should be removed after we find a better way
# to do this
# node_message_factory.update_schemas_by_field_type(
#     PLedgerIdField, LedgerIdField)
# node_message_factory.update_schemas_by_field_type(
#     PLedgerInfoField, LedgerInfoField)


class SafeRequest(Request, ClientMessageValidator):

    def __init__(self, **kwargs):
        ClientMessageValidator.__init__(self, operation_schema_is_strict=True,
                                        schema_is_strict=False)
        self.validate(kwargs)
        Request.__init__(self, **kwargs)
