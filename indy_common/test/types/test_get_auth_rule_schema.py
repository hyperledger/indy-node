from collections import OrderedDict

from indy_common.types import ClientSchemaOperation, SchemaField, ConstraintListField, ClientAuthRuleOperation, \
    ConstraintEntityField, ConstraintField
from plenum.common.messages.fields import ConstantField, VersionField, IterableField, LimitedLengthStringField, \
    ChooseField, RoleField, NonNegativeNumberField, BooleanField, AnyMapField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("auth_action", ChooseField),
    ("auth_type", LimitedLengthStringField),
    ("field", LimitedLengthStringField),
    ("old_value", LimitedLengthStringField),
    ("new_value", LimitedLengthStringField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientAuthRuleOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientAuthRuleOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
