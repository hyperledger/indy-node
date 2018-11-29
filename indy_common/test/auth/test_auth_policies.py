import pytest

from indy_common.auth_rules import RuleAdd, RuleRemove, RuleEdit, AuthConstraint, RoleDef, LocalAuthPolicy


@pytest.fixture(scope='function', params=[RuleAdd, RuleRemove, RuleEdit])
def not_allow_all_dict(request):
    return request.param, dict(description="General rule",
                               txn_type="SomeTxn",
                               default_auth_constraint=AuthConstraint([RoleDef('TRUSTEE', 3)]),
                               rule_id='',
                               field='some_field',
                               old_value='old_value',
                               new_value='new_value')


def test_local_policy_get_default_constraints(not_allow_all_dict):
    rule_cls, rule_dict = not_allow_all_dict
    rule = rule_cls(**rule_dict)
    policy = LocalAuthPolicy({rule.rule_id: rule.default_auth_constraint})
    assert policy.get_auth_constraint(rule.rule_id) == AuthConstraint([RoleDef('TRUSTEE', 3)])
