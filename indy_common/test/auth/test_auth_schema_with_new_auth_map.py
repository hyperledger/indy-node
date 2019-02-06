from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.constants import SCHEMA


def test_schema_adding(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier", "trust_anchor_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=SCHEMA,
                                                                 field='some_field',
                                                                 value='some_value',
                                                                 is_owner=is_owner)])


def test_schema_editing(write_request_validation, req, is_owner):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=SCHEMA,
                                                        field='some_field',
                                                        old_value='old_value',
                                                        new_value='new_value',
                                                        is_owner=is_owner)])
