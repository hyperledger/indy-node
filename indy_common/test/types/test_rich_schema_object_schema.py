from collections import OrderedDict

import pytest

from indy_common.types import ClientJsonLdContextOperation, ClientRichSchemaOperation, \
    ClientRichSchemaEncodingOperation, ClientRichSchemaMappingOperation, ClientRichSchemaCredDefOperation, \
    ClientRichSchemaPresDefOperation
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, NonEmptyStringField, VersionField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ver", LimitedLengthStringField),
    ("id", NonEmptyStringField),
    ("rsType", ConstantField),
    ("rsName", LimitedLengthStringField),
    ("rsVersion", VersionField),
    ("content", NonEmptyStringField),
])


@pytest.mark.parametrize('operation_class',
                         [ClientJsonLdContextOperation, ClientRichSchemaOperation, ClientRichSchemaEncodingOperation,
                          ClientRichSchemaMappingOperation,
                          ClientRichSchemaCredDefOperation,
                          ClientRichSchemaPresDefOperation])
def test_has_expected_fields(operation_class):
    actual_field_names = OrderedDict(operation_class.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


@pytest.mark.parametrize('operation_class, txn_type, rs_type',
                         [(ClientJsonLdContextOperation, "200", 'ctx'),
                          (ClientRichSchemaOperation, "201", 'sch'),
                          (ClientRichSchemaEncodingOperation, "202", 'enc'),
                          (ClientRichSchemaMappingOperation, "203", 'map'),
                          (ClientRichSchemaCredDefOperation, "204", 'cdf'),
                          (ClientRichSchemaPresDefOperation, "205", 'pdf')])
def test_has_expected_validators(operation_class, txn_type, rs_type):
    schema = dict(operation_class.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
    assert schema["rsType"].value == rs_type
    assert schema["type"].value == txn_type
