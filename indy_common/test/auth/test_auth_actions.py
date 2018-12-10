from indy_common.auth_actions import compile_action_id, ADD_PREFIX, EDIT_PREFIX


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
