from collections import OrderedDict
from indy_common.types import ClientGetRsEncodingOperation, RsEncodingMetaField
from plenum.common.messages.fields import ConstantField, IdentifierField, VersionField, LimitedLengthStringField


EXPECTED_ORDERED_FIELDS_SCHEMA = OrderedDict([
    ("type", ConstantField),
    ("name", LimitedLengthStringField),
    ("version", VersionField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsEncodingMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_SCHEMA.keys()


def test_has_expected_validators_s():
    schema = dict(RsEncodingMetaField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_SCHEMA.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("from", IdentifierField),
    ("meta", RsEncodingMetaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetRsEncodingOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetRsEncodingOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
