import pytest
from indy_common.types import ClientPoolUpgradeOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, ChooseField, VersionField, MapField, Sha256HexField, \
    NonNegativeNumberField, LimitedLengthStringField, BooleanField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ('action', ChooseField),
    ("version", VersionField),
    ('schedule', MapField),
    ('sha256', Sha256HexField),
    ('timeout', NonNegativeNumberField),
    ('justification', LimitedLengthStringField),
    ("name", LimitedLengthStringField),
    ("force", BooleanField),
    ("reinstall", BooleanField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientPoolUpgradeOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientPoolUpgradeOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
