from collections import OrderedDict

from indy_common.types import ClientSetFeesOperation, SetFeesField
from plenum.common.messages.fields import ConstantField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("fees", SetFeesField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetFeesOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetFeesOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
