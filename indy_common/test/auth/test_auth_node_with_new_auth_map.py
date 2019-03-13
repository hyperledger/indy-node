from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from plenum.common.constants import SERVICES, NODE, NODE_IP, NODE_PORT, CLIENT_PORT, \
    CLIENT_IP, BLS_KEY, ALIAS


def test_node_enable(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NODE,
                                                                 field=SERVICES,
                                                                 value='[\'VALIDATOR\']',
                                                                 is_owner=is_owner)])


def test_node_enable_with_empty_services(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionAdd(txn_type=NODE,
                                                                 field=SERVICES,
                                                                 value=[],
                                                                 is_owner=is_owner)])


def test_node_promote(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner) or (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=SERVICES,
                                                                  old_value=[],
                                                                  new_value=['VALIDATOR'],
                                                                  is_owner=is_owner)])


def test_node_demote(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner) or (req.identifier == "trustee_identifier")
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=SERVICES,
                                                                  old_value=['VALIDATOR'],
                                                                  new_value=[],
                                                                  is_owner=is_owner)])


def test_node_wrong_old_service_name(write_request_validation, req, is_owner):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=NODE,
                                                        field=SERVICES,
                                                        old_value='aaa',
                                                        new_value=[],
                                                        is_owner=is_owner)])


def test_node_wrong_new_service_name(write_request_validation, req, is_owner):
    assert not write_request_validation(req,
                                        [AuthActionEdit(txn_type=NODE,
                                                        field=SERVICES,
                                                        old_value=[],
                                                        new_value='aaa',
                                                        is_owner=is_owner)])


def test_node_change_node_ip(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=NODE_IP,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])


def test_node_change_node_port(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=NODE_PORT,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])


def test_node_change_client_ip(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=CLIENT_IP,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])


def test_node_change_client_port(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=CLIENT_PORT,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])


def test_node_change_bls_keys(write_request_validation, req, is_owner):
    authorized = (req.identifier == "steward_identifier" and is_owner)
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=BLS_KEY,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])


def test_node_change_alias(write_request_validation, req, is_owner):
    authorized = False  # alias can not be changed
    assert authorized == write_request_validation(req,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=ALIAS,
                                                                  old_value='old_value',
                                                                  new_value='new_value',
                                                                  is_owner=is_owner)])
