import pytest

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.constants import SET_JSON_LD_CONTEXT, SET_RICH_SCHEMA, SET_RICH_SCHEMA_ENCODING, \
    SET_RICH_SCHEMA_MAPPING, SET_RICH_SCHEMA_CRED_DEF


@pytest.mark.parametrize('txn_type',
                         [SET_JSON_LD_CONTEXT, SET_RICH_SCHEMA, SET_RICH_SCHEMA_ENCODING, SET_RICH_SCHEMA_MAPPING,
                          SET_RICH_SCHEMA_CRED_DEF])
def test_rich_schema_object_adding(write_request_validation, req, is_owner, txn_type):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier", "endorser_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=txn_type,
                                                                 field='some_field',
                                                                 value='some_value',
                                                                 is_owner=is_owner)])


@pytest.mark.parametrize('txn_type',
                         [SET_JSON_LD_CONTEXT, SET_RICH_SCHEMA, SET_RICH_SCHEMA_ENCODING, SET_RICH_SCHEMA_MAPPING,
                          SET_RICH_SCHEMA_CRED_DEF])
def test_rich_schema_object_editing(write_request_validation, req, is_owner, txn_type):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=txn_type,
                                                        field='some_field',
                                                        old_value='old_value',
                                                        new_value='new_value',
                                                        is_owner=is_owner)])
