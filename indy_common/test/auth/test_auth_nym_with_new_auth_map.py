import pytest
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from plenum.common.constants import TRUSTEE, STEWARD, VERKEY

from indy_common.constants import ROLE, NYM, TRUST_ANCHOR


@pytest.fixture(scope='module', params=[True, False])
def is_owner(request):
    return request.param


def test_make_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NYM,
                                                                 field=ROLE,
                                                                 value=TRUSTEE,
                                                                 is_owner=is_owner)])


def test_make_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NYM,
                                                                 field=ROLE,
                                                                 value=STEWARD,
                                                                 is_owner=is_owner)])


def test_make_trust_anchor(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NYM,
                                                                 field=ROLE,
                                                                 value=TRUST_ANCHOR,
                                                                 is_owner=is_owner)])


def test_remove_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


def test_remove_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


def test_remove_trust_anchor(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUST_ANCHOR,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


def test_change_verkey(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=VERKEY,
                                                                  old_value="_verkey".format(req.identifier),
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])
