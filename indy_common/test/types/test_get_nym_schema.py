import pytest
from indy_common.types import ClientGetNymOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, IdentifierField, IntegerField, TxnSeqNoField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ("timestamp", IntegerField),
    ("seqNo", TxnSeqNoField)
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetNymOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetNymOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
