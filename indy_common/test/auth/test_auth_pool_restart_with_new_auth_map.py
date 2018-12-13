from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.constants import ACTION, POOL_RESTART


def test_pool_restart_add_action(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=POOL_RESTART,
                                                                 field=ACTION,
                                                                 value='start',
                                                                 is_owner=is_owner)])
