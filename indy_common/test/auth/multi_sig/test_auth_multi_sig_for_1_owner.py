import pytest

from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER


@pytest.fixture(scope='module')
def write_auth_req_validator(write_auth_req_validator, key):
    write_auth_req_validator.auth_cons_strategy.get_auth_constraint = lambda a: AuthConstraint(IDENTITY_OWNER, 1)
    return write_auth_req_validator


def test_claim_def_adding_success_1_owner(write_request_validation, req,
                                          identity_owners, key):
    req.signatures = {identity_owners[0]: "signature"}
    assert write_request_validation(req, [key])


def test_claim_def_adding_success_2_owner(write_request_validation, req,
                                          identity_owners, key):
    req.signatures = {idr: "signature" for idr in identity_owners[:2]}
    assert write_request_validation(req, [key])


def test_claim_def_adding_fail_1_trustee(write_request_validation, req,
                                         trustees, key):
    req.signatures = {trustees[0]: "signature"}
    assert not write_request_validation(req, [key])
