from collections import OrderedDict

from indy_common.types import ClientSchemaOperation, SchemaField, ConstraintListField, ClientAuthRuleOperation, \
    ConstraintEntityField, ConstraintField, AuthRuleValueField
from plenum.common.messages.fields import ConstantField, VersionField, IterableField, LimitedLengthStringField, \
    ChooseField, RoleField, NonNegativeNumberField, BooleanField, AnyMapField

# ConstraintListField
EXPECTED_ORDERED_FIELDS_CONSTRAINT_LIST = OrderedDict([
    ("constraint_id", ChooseField),
    ("auth_constraints", IterableField),
])


def test_has_expected_fields_list():
    actual_field_names = OrderedDict(ConstraintListField().schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_CONSTRAINT_LIST.keys()


def test_has_expected_validators_list():
    schema = dict(ConstraintListField().schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_CONSTRAINT_LIST.items():
        assert isinstance(schema[field], validator)


# ConstraintEntityField
EXPECTED_ORDERED_FIELDS_CONSTRAINT_ENTITY = OrderedDict([
    ("constraint_id", ChooseField),
    ("role", RoleField),
    ("sig_count", NonNegativeNumberField),
    ("need_to_be_owner", BooleanField),
    ("off_ledger_signature", BooleanField),
    ("metadata", AnyMapField),
])


def test_has_expected_fields_entity():
    actual_field_names = OrderedDict(ConstraintEntityField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_CONSTRAINT_ENTITY.keys()


def test_has_expected_validators_entity():
    schema = dict(ConstraintEntityField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_CONSTRAINT_ENTITY.items():
        assert isinstance(schema[field], validator)


# ClientAuthRuleOperation
EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("constraint", ConstraintField),
    ("auth_action", ChooseField),
    ("auth_type", LimitedLengthStringField),
    ("field", LimitedLengthStringField),
    ("old_value", AuthRuleValueField),
    ("new_value", AuthRuleValueField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientAuthRuleOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientAuthRuleOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
