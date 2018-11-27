import pytest

from indy_common.auth_rules import AuthRule


@pytest.fixture(scope='function')
def rule_dict():
    return dict(typ='1',
                field='',
                prev_value='',
                new_value='',
                who_can=[],
                count_of_signatures=1,
                description='Rule for testing purposes')


def test_allow_with_empty_field(rule_dict):
    rule = AuthRule(**rule_dict)
    assert rule.is_rule_accepted(field='',
                                 prev_value='',
                                 new_value='',
                                 actor_role='1',
                                 count_of_signatures=1)


def test_allow_with_not_empty_field(rule_dict):
    rule = AuthRule(**rule_dict)
    assert rule.is_rule_accepted(field='abs',
                                 prev_value='',
                                 new_value='',
                                 actor_role='1',
                                 count_of_signatures=1)


def test_not_allow_for_different_field(rule_dict):
    rule_dict['field'] = 'abc'
    rule = AuthRule(**rule_dict)
    assert not rule.is_rule_accepted(field='def',
                                     prev_value='',
                                     new_value='',
                                     actor_role='1',
                                     count_of_signatures=1)