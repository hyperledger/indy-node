from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import ConstraintCreator
from indy_common.constants import AUTH_ACTION, OLD_VALUE, NEW_VALUE, AUTH_TYPE, FIELD, CONSTRAINT
from plenum.common.exceptions import InvalidClientRequest


class StaticAuthRuleHelper:

    @staticmethod
    def get_auth_key(operation):
        action = operation.get(AUTH_ACTION, None)
        old_value = operation.get(OLD_VALUE, None)
        new_value = operation.get(NEW_VALUE, None)
        auth_type = operation.get(AUTH_TYPE, None)
        field = operation.get(FIELD, None)

        return AuthActionEdit(txn_type=auth_type,
                              field=field,
                              old_value=old_value,
                              new_value=new_value).get_action_id() \
            if action == EDIT_PREFIX else \
            AuthActionAdd(txn_type=auth_type,
                          field=field,
                          value=new_value).get_action_id()

    @staticmethod
    def get_auth_constraint(operation):
        return ConstraintCreator.create_constraint(operation.get(CONSTRAINT))

    @staticmethod
    def check_auth_key(operation, identifier, req_id, auth_map):
        auth_key = StaticAuthRuleHelper.get_auth_key(operation)

        if auth_key not in auth_map:
            raise InvalidClientRequest(identifier, req_id,
                                       "Unknown authorization rule: key '{}' is not "
                                       "found in authorization map.".format(auth_key))
