import pytest

from indy_common.auth_rules import RuleAdd, RuleRemove, RuleEdit, Authorizer, AuthConstraint, RoleDef, AuthRuleNotFound
from indy_common.constants import LOCAL_AUTH_POLICY
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope='function', params=[RuleAdd, RuleRemove, RuleEdit])
def all_rule_classes(request):
    return request.param


@pytest.fixture(scope='module')
def fake_config():
    return FakeSomething(authPolicy=LOCAL_AUTH_POLICY)


def test_find_rule_and_authorize_with_any_field(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='*',
                            old_value='old_value',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value',
                                auth_constraint=auth_constraint)


def test_find_rule_and_authorize_with_any_old_value(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='*',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value',
                                auth_constraint=auth_constraint)


def test_find_rule_and_authorize_with_any_new_value(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='old_value',
                            new_value='*')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value',
                                auth_constraint=auth_constraint)


def test_find_rule_and_authorize_with_any_field_and_values(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='*',
                            old_value='*',
                            new_value='*')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value',
                                auth_constraint=auth_constraint)


def test_find_rule_and_authorize_with_the_same_field_and_values(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='old_value',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='old_value',
                                new_value='new_value',
                                auth_constraint=auth_constraint)


def test_not_find_rule_and_authorize_with_different_field_or_values(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='old_value',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert not authorizer.find_rule(txn_type='SomeType',
                                    field='some_other_field',
                                    old_value='old_value',
                                    new_value='new_value')

    assert not authorizer.find_rule(txn_type='SomeType',
                                    field='some_field',
                                    old_value='other_old_value',
                                    new_value='new_value')

    assert not authorizer.find_rule(txn_type='SomeType',
                                    field='some_field',
                                    old_value='old_value',
                                    new_value='other_new_value')


def test_find_rule_and_authorize_for_values_with_brackets(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='[old_value]',
                            new_value='[new_value]')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    assert authorizer.find_rule(txn_type='SomeType',
                                field='some_field',
                                old_value='[old_value]',
                                new_value='[new_value]') == rule
    assert authorizer.authorize(txn_type='SomeType',
                                field='some_field',
                                old_value='[old_value]',
                                new_value='[new_value]',
                                auth_constraint=auth_constraint)


def test_not_authorized(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=3)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='old_value',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    """Not authorized because of sig_count"""
    assert not authorizer.authorize(txn_type='SomeType',
                                    field='some_field',
                                    old_value='old_value',
                                    new_value='new_value',
                                    auth_constraint=AuthConstraint([RoleDef(role='Actor', sig_count=2)]))

    """Not authorized because of different Role"""
    assert not authorizer.authorize(txn_type='SomeType',
                                    field='some_field',
                                    old_value='old_value',
                                    new_value='new_value',
                                    auth_constraint=AuthConstraint([RoleDef(role='OtherActor', sig_count=3)]))

    """Not authorized because of different Role and sig_count"""
    assert not authorizer.authorize(txn_type='SomeType',
                                    field='some_field',
                                    old_value='old_value',
                                    new_value='new_value',
                                    auth_constraint=AuthConstraint([RoleDef(role='OtherActor', sig_count=2)]))


def test_raise_error_if_rule_not_found(all_rule_classes, fake_config):
    auth_constraint = AuthConstraint([RoleDef(role='Actor', sig_count=1)])
    rule = all_rule_classes(description='Some rule', txn_type='SomeType',
                            default_auth_constraint=auth_constraint,
                            field='some_field',
                            old_value='old_value',
                            new_value='new_value')
    auth_map = {rule.rule_id: rule}
    authorizer = Authorizer(auth_map=auth_map,
                            config=fake_config)
    with pytest.raises(AuthRuleNotFound, match="There is no rule for txn_type"):
        authorizer.authorize(txn_type='SomeType',
                             field='some_other_field',
                             old_value='old_value',
                             new_value='new_value',
                             auth_constraint=auth_constraint)
