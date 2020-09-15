from collections import OrderedDict

import pytest

from indy_common.types import ClientGetRichSchemaObjectByMetadataOperation
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, VersionField, NonEmptyStringField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("rsType", NonEmptyStringField),
    ("rsName", LimitedLengthStringField),
    ("rsVersion", VersionField),
])


@pytest.mark.types
def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetRichSchemaObjectByMetadataOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


@pytest.mark.types
def test_has_expected_validators():
    schema = dict(ClientGetRichSchemaObjectByMetadataOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
