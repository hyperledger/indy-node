#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import pytest
from indy_common.types import ClientSchemaOperation, SchemaField
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, VersionField, IterableField, LimitedLengthStringField

EXPECTED_ORDERED_FIELDS_SCHEMA = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("attr_names", IterableField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(SchemaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_SCHEMA.keys()


def test_has_expected_validators_s():
    schema = dict(SchemaField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_SCHEMA.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("data", SchemaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSchemaOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSchemaOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
