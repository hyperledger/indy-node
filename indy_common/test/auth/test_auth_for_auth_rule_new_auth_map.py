from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.constants import POOL_CONFIG, ACTION, AUTH_RULE


def test_auth_rule(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=AUTH_RULE,
                                                                  field=ACTION,  # TODO: change to real field name
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])
