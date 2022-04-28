import pytest
from indy_common.types import ClientGetAttribOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, IntegerField, LimitedLengthStringField, IdentifierField, Sha256HexField, TxnSeqNoField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ("raw", LimitedLengthStringField),
    ('enc', LimitedLengthStringField),
    ('hash', Sha256HexField),
    ('timestamp', IntegerField),
    ('seqNo', TxnSeqNoField)
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetAttribOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetAttribOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
