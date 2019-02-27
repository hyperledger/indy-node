from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.constants import VALIDATOR_INFO


def test_pool_restart_add_action(write_request_validation, is_owner, req):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier", "network_monitor_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=VALIDATOR_INFO,
                                                                 field='some_field',
                                                                 value='some_value',
                                                                 is_owner=is_owner)])
