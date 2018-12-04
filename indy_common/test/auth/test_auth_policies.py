from indy_common.auth_rules import AuthConstraint, RoleDef, LocalAuthPolicy


def test_local_policy_get_default_constraints(not_allow_all_dict):
    rule_cls, rule_dict = not_allow_all_dict
    rule = rule_cls(**rule_dict)
    policy = LocalAuthPolicy({rule.rule_id: rule})
    assert policy.get_auth_constraint(rule.rule_id) == AuthConstraint([RoleDef('TRUSTEE', 3)])
