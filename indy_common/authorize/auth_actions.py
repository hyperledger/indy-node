from typing import NamedTuple


from abc import ABCMeta, abstractmethod


RULE_DELIMETER = "--"
ADD_PREFIX = "ADD"
EDIT_PREFIX = "EDIT"

ActionDef = NamedTuple('ActionDef', [('prefix', str), ('txn_type', str), ('field', str), ('old_value', str), ('new_value', str)])


def compile_action_id(txn_type,
                      field,
                      old_value,
                      new_value,
                      prefix='') -> str:
    return RULE_DELIMETER.join([prefix,
                                txn_type,
                                field,
                                old_value,
                                new_value])


def split_action_id(action_id) -> ActionDef:
    return ActionDef(*action_id.split(RULE_DELIMETER))


"""

Action's classes

"""


class AbstractAuthAction(metaclass=ABCMeta):
    def __init__(self, txn_type):
        pass

    @abstractmethod
    def get_action_id(self):
        raise NotImplementedError()


class AuthActionAdd(AbstractAuthAction):
    def __init__(self, txn_type, field=None, value=None, is_owner=True):
        self.txn_type = txn_type
        self.field = field
        self.value = value
        self.is_owner = is_owner

    def get_action_id(self):
        return compile_action_id(txn_type=self.txn_type,
                                 field=self.field,
                                 old_value='*',
                                 new_value=self.value,
                                 prefix=ADD_PREFIX)


class AuthActionEdit(AbstractAuthAction):
    def __init__(self, txn_type, field=None, old_value=None, new_value=None, is_owner=True):
        self.txn_type = txn_type
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.is_owner = is_owner

    def get_action_id(self):
        return compile_action_id(txn_type=self.txn_type,
                                 field=self.field,
                                 old_value=self.old_value,
                                 new_value=self.new_value,
                                 prefix=EDIT_PREFIX)
