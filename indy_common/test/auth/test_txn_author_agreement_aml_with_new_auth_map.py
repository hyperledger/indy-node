from indy_common.authorize.auth_actions import AuthActionAdd
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_AML


def test_taa_aml_with_new_auth_map(write_request_validation, is_owner, req):
    authorized = req.identifier == "trustee_identifier"
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=TXN_AUTHOR_AGREEMENT_AML,
                                                                 field='some_field',
                                                                 value='some_value',
                                                                 is_owner=is_owner)])
