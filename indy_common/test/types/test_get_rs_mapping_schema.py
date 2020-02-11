from collections import OrderedDict

from indy_common.types import ClientGetRsMappingOperation, RsMappingMetaField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, IdentifierField, \
    VersionField

EXPECTED_ORDERED_META = OrderedDict([
    ("type", ConstantField),
    ("name", LimitedLengthStringField),
    ("version", VersionField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsMappingMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_META.keys()


def test_has_expected_validators_s():
    schema = dict(RsMappingMetaField.schema)
    for field, validator in EXPECTED_ORDERED_META.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("from", IdentifierField),
    ("meta", RsMappingMetaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetRsMappingOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetRsMappingOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
