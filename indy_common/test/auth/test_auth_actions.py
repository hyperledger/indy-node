from indy_common.authorize.auth_actions import compile_action_id, ADD_PREFIX, EDIT_PREFIX, split_action_id, ActionDef


def test_get_action_id_action_add(action_add):
    assert action_add.get_action_id() == compile_action_id(txn_type='SomeType',
                                                           field='some_field',
                                                           old_value='*',
                                                           new_value='new_value',
                                                           prefix=ADD_PREFIX)


def test_get_action_id_action_edit(action_edit):
    assert action_edit.get_action_id() == compile_action_id(txn_type='SomeType',
                                                            field='some_field',
                                                            old_value='old_value',
                                                            new_value='new_value',
                                                            prefix=EDIT_PREFIX)


def test_split_action_id():
    origin = ActionDef('SomeType', 'PREFIX', 'some_field', 'old_value', 'new_value')
    splitted_action = split_action_id(compile_action_id(txn_type='SomeType',
                                                        field='some_field',
                                                        old_value='old_value',
                                                        new_value='new_value',
                                                        prefix='PREFIX'))
    assert origin.prefix == splitted_action.prefix
    assert origin.txn_type == splitted_action.txn_type
    assert origin.field == splitted_action.field
    assert origin.old_value == splitted_action.old_value
    assert origin.new_value == splitted_action.new_value
