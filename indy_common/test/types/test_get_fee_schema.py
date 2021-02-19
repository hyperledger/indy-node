from collections import OrderedDict

from indy_common.types import ClientGetFeeOperation
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("alias", LimitedLengthStringField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetFeeOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetFeeOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
