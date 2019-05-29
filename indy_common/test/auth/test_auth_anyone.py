import pytest

from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.types import Request

action = AuthActionEdit(txn_type="some_type",
                        field='some_field',
                        old_value='old_value',
                        new_value='new_value')


@pytest.fixture(scope='module')
def write_auth_req_validator(write_auth_req_validator):
    write_auth_req_validator.auth_map[action.get_action_id()] = AuthConstraint(role="*",
                                                                               sig_count=0)
    return write_auth_req_validator


def test_auth_request_without_signatures(write_request_validation):
    req = Request(identifier="UnknownIdr",
                  operation={})
    assert write_request_validation(req,
                                    [action])
