import pytest

from indy_common.auth import Authoriser, generate_auth_map
from indy_common.auth_rules import AuthConstraint, RoleDef, RuleAdd, RuleRemove, RuleEdit
from plenum.common.constants import STEWARD, TRUSTEE

from indy_common.constants import TRUST_ANCHOR


@pytest.fixture(scope='function', params=[STEWARD, TRUSTEE, TRUST_ANCHOR, None])
def role(request):
    return request.param


@pytest.fixture(scope='function', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(scope='function', params=[None, "value1"])
def old_values(request):
    return request.param


@pytest.fixture(scope='module')
def initialized_auth_map():
    Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles, False)



@pytest.fixture(scope='function')
def dict_add():
    return dict(description="Adding something",
                txn_type="SomeTxn",
                default_auth_constraint=AuthConstraint([RoleDef('TRUSTEE', 3)]),
                rule_id='',
                field='some_field',
                old_value='old_value',
                new_value='new_value')


@pytest.fixture(scope='function')
def dict_remove():
    return dict(description="Removing something",
                txn_type="SomeTxn",
                default_auth_constraint=AuthConstraint([RoleDef('TRUSTEE', 3)]),
                rule_id='',
                field='some_field',
                old_value='old_value',
                new_value='new_value')


@pytest.fixture(scope='function')
def dict_edit():
    return dict(description="Editing something",
                txn_type="SomeTxn",
                default_auth_constraint=AuthConstraint([RoleDef('TRUSTEE', 3)]),
                rule_id='',
                field='some_field',
                old_value='old_value',
                new_value='new_value')


@pytest.fixture(scope='function', params=[RuleAdd, RuleRemove, RuleEdit])
def allow_all_dict(request):
    return request.param, dict(description="General rule",
                               txn_type="SomeTxn",
                               default_auth_constraint=AuthConstraint([]),
                               rule_id='')


@pytest.fixture(scope='function', params=[RuleAdd, RuleRemove, RuleEdit])
def not_allow_all_dict(request):
    return request.param, dict(description="General rule",
                               txn_type="SomeTxn",
                               default_auth_constraint=AuthConstraint([RoleDef('TRUSTEE', 3)]),
                               rule_id='',
                               field='some_field',
                               old_value='old_value',
                               new_value='new_value')



