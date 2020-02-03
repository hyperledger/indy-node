from collections import OrderedDict

from indy_common.types import ClientGetRsCredDefOperation, RsCredDefMetaField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, IdentifierField, \
    VersionField

EXPECTED_ORDERED_META = OrderedDict([
    ("type", ConstantField),
    ("name", LimitedLengthStringField),
    ("version", VersionField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsCredDefMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_META.keys()


def test_has_expected_validators_s():
    schema = dict(RsCredDefMetaField.schema)
    for field, validator in EXPECTED_ORDERED_META.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("from", IdentifierField),
    ("meta", RsCredDefMetaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetRsCredDefOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetRsCredDefOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)