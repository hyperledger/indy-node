import pytest
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from plenum.common.constants import TRUSTEE, STEWARD, VERKEY

from indy_common.constants import ROLE, NYM, ENDORSER, NETWORK_MONITOR


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


def test_make_endorser(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NYM,
                                                                 field=ROLE,
                                                                 value=ENDORSER,
                                                                 is_owner=is_owner)])


def test_make_network_monitor(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NYM,
                                                                 field=ROLE,
                                                                 value=NETWORK_MONITOR,
                                                                 is_owner=is_owner)])


# Trustee tests
def test_change_trustee_to_trustee(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value=TRUSTEE,
                                                                  is_owner=is_owner)])


def test_change_trustee_to_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value=STEWARD,
                                                                  is_owner=is_owner)])


def test_change_trustee_to_endorser(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value=ENDORSER,
                                                                  is_owner=is_owner)])


def test_change_trustee_to_network_monitor(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value=NETWORK_MONITOR,
                                                                  is_owner=is_owner)])


def test_change_trustee_to_identity_owner(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=TRUSTEE,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


# Steward tests
def test_change_steward_to_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value=TRUSTEE,
                                                                  is_owner=is_owner)])


def test_change_steward_to_steward(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value=STEWARD,
                                                                  is_owner=is_owner)])


def test_change_steward_to_endorser(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value=ENDORSER,
                                                                  is_owner=is_owner)])


def test_change_steward_to_network_monitor(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value=NETWORK_MONITOR,
                                                                  is_owner=is_owner)])


def test_change_steward_to_identity_owner(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=STEWARD,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


# Endorser tests
def test_change_endorser_to_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=ENDORSER,
                                                                  new_value=TRUSTEE,
                                                                  is_owner=is_owner)])


def test_change_endorser_to_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=ENDORSER,
                                                                  new_value=STEWARD,
                                                                  is_owner=is_owner)])


def test_change_endorser_to_endorser(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=ENDORSER,
                                                                  new_value=ENDORSER,
                                                                  is_owner=is_owner)])


def test_change_endorser_to_network_monitor(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=ENDORSER,
                                                                  new_value=NETWORK_MONITOR,
                                                                  is_owner=is_owner)])


def test_change_endorser_to_identity_owner(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=ENDORSER,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


# Network Monitor tests
def test_change_network_monitor_to_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=NETWORK_MONITOR,
                                                                  new_value=TRUSTEE,
                                                                  is_owner=is_owner)])


def test_change_network_monitor_to_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=NETWORK_MONITOR,
                                                                  new_value=STEWARD,
                                                                  is_owner=is_owner)])


def test_change_network_monitor_to_endorser(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=NETWORK_MONITOR,
                                                                  new_value=ENDORSER,
                                                                  is_owner=is_owner)])


def test_change_network_monitor_to_network_monitor(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=NETWORK_MONITOR,
                                                                  new_value=NETWORK_MONITOR,
                                                                  is_owner=is_owner)])


def test_change_network_monitor_to_identity_owner(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value=NETWORK_MONITOR,
                                                                  new_value='',
                                                                  is_owner=is_owner)])


# Identity Owner tests
def test_change_identity_owner_to_trustee(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value='',
                                                                  new_value=TRUSTEE,
                                                                  is_owner=is_owner)])


def test_change_identity_owner_to_steward(write_request_validation, req, is_owner):
    authorized = (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value='',
                                                                  new_value=STEWARD,
                                                                  is_owner=is_owner)])


def test_change_identity_owner_to_endorser(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value='',
                                                                  new_value=ENDORSER,
                                                                  is_owner=is_owner)])


def test_change_identity_owner_to_network_monitor(write_request_validation, req, is_owner):
    authorized = req.identifier in ("trustee_identifier", "steward_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value='',
                                                                  new_value=NETWORK_MONITOR,
                                                                  is_owner=is_owner)])


def test_change_identity_owner_to_identity_owner(write_request_validation, req, is_owner):
    authorized = is_owner
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=ROLE,
                                                                  old_value='',
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
