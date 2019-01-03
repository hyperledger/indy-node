from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.constants import POOL_CONFIG, ACTION


def test_pool_config_change(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=POOL_CONFIG,
                                                                  field=ACTION,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])
