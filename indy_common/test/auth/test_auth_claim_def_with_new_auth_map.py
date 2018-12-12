from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit

from indy_common.constants import CLAIM_DEF


def test_claim_def_adding(write_auth_req_validator, req, is_owner):
    assert write_auth_req_validator.validate(req,
                                             [AuthActionAdd(txn_type=CLAIM_DEF,
                                                            field='some_field',
                                                            value='some_value')],
                                             is_owner=is_owner)


def test_claim_def_editing(write_auth_req_validator, req, is_owner):
    authorized = is_owner
    assert authorized == write_auth_req_validator.validate(req,
                                                           [AuthActionEdit(txn_type=CLAIM_DEF,
                                                                           field='some_field',
                                                                           old_value='old_value',
                                                                           new_value='new_value')],
                                                           is_owner=is_owner)
