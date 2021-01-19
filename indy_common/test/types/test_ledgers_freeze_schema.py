from collections import OrderedDict

from indy_common.types import ClientLedgersFreezeOperation
from plenum.common.messages.fields import ConstantField, IterableField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ledgers_ids", IterableField)
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientLedgersFreezeOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientLedgersFreezeOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
