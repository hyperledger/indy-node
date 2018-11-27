from indy_common.constants import NYM
from plenum.common.constants import TRUSTEE, STEWARD

from abc import ABCMeta, abstractmethod

from indy_common.constants import OWNER, POOL_UPGRADE, TRUST_ANCHOR, NYM, \
    POOL_CONFIG, SCHEMA, CLAIM_DEF, \
    POOL_RESTART, VALIDATOR_INFO


class AuthRule:
    def __init__(self,
                 typ: str,
                 field: str,
                 prev_value: str,
                 new_value: str,
                 who_can: str,
                 count_of_signatures: int,
                 description: str):
        self.type = typ
        self.field = field
        self.prev_value = prev_value
        self.new_value = new_value
        self.who_can = who_can
        self.count_of_signatures = count_of_signatures
        self.description = description
        self.allow_field = False
        self.allow_prev_value = False
        self.allow_new_value = False
        self.allow_for_all = False
        self._validate_fields()
        self._preprocessing()

    def _preprocessing(self):
        if self.field == '':
            self.allow_field = True
        if self.prev_value == '' or self.prev_value == '*':
            self.allow_prev_value = True
        if self.new_value == '*':
            self.allow_new_value = True
        if self.who_can == []:
            self.allow_for_all = True


    def _validate_fields(self):
        if not isinstance(self.field, str) or \
                not isinstance(self.prev_value, str) or \
                not isinstance(self.new_value, str) or \
                not isinstance(self.who_can, list) or \
                not isinstance(self.count_of_signatures, int):
            return False

        return True

    def is_rule_accepted(self,
                         field: str,
                         prev_value: str,
                         new_value: str,
                         actor_role: str,
                         count_of_signatures: int):
        if not self.allow_field and self.field != field:
            return False
        if not self.allow_prev_value and self.prev_value != prev_value:
            return False
        if not self.allow_new_value and self.new_value != new_value:
            return False
        if not self.allow_for_all and actor_role not in self.who_can:
            return False
        if count_of_signatures < self.count_of_signatures:
            return False
        return True


addNewTrustee = dict(typ=NYM,
                     field='role',
                     prev_value='',
                     new_value=TRUSTEE,
                     who_can=[TRUSTEE],
                     count_of_signatures=1,
                     desctiprion="Add new trustee")

addNewSteward = dict(typ=NYM,
                     field='role',
                     prev_value='',
                     new_value=STEWARD,
                     who_can=[TRUSTEE],
                     count_of_signatures=1,
                     description="Add new steward")
