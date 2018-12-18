from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.constants import POOL_CONFIG, ACTION


def test_pool_config_change(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=POOL_CONFIG,
                                                                 field=ACTION,
                                                                 value='value',
                                                                 is_owner=is_owner)])
