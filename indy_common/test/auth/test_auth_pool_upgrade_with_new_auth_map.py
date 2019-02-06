from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.constants import POOL_UPGRADE, ACTION


def test_pool_upgrade_start(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=POOL_UPGRADE,
                                                                 field=ACTION,
                                                                 value='start',
                                                                 is_owner=is_owner)])


def test_pool_upgrade_cancel(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=POOL_UPGRADE,
                                                                  field=ACTION,
                                                                  old_value='start',
                                                                  new_value='cancel',
                                                                  is_owner=is_owner)])


def test_pool_upgrade_cancel_wrong_new_value(write_request_validation, is_owner, req):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=POOL_UPGRADE,
                                                        field=ACTION,
                                                        old_value='start',
                                                        new_value='aa_cancel_aa',
                                                        is_owner=is_owner)])


def test_pool_upgrade_cancel_wrong_old_value(write_request_validation, is_owner, req):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=POOL_UPGRADE,
                                                        field=ACTION,
                                                        old_value='not_start',
                                                        new_value='cancel',
                                                        is_owner=is_owner)])
