from collections import OrderedDict
from indy_common.types import ClientGetRsEncodingOperation
from plenum.common.messages.fields import ConstantField, IdentifierField


EXPECTED_GET_ENCODING_OP_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(ClientGetRsEncodingOperation.schema).keys()
    assert actual_field_names == EXPECTED_GET_ENCODING_OP_FIELDS.keys()


def test_has_expected_validators_s():
    schema = dict(ClientGetRsEncodingOperation.schema)
    for field, validator in EXPECTED_GET_ENCODING_OP_FIELDS.items():
        assert isinstance(schema[field], validator)

