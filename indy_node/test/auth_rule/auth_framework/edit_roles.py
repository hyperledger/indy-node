import random

import pytest

from indy_common.authorize import auth_map
from indy_common.authorize.auth_constraints import accepted_roles, ConstraintsEnum, \
    AuthConstraint
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest, AddNewStewardTest, \
    AddNewEndorserTest, AddNewIdentityOwnerTest, AddNewNetworkMonitorTest
from indy_node.test.auth_rule.auth_framework.basic import roles_to_string, AuthTest
from plenum.common.exceptions import RequestRejectedException

from indy_node.test.helper import build_auth_rule_request_json


class EditRoleTest(AuthTest):
    def __init__(self, action_id, env, add_new_role_cls):
        super().__init__(env, action_id)
        constraint = auth_map.auth_map[action_id]
        self.constraint = constraint
        self.role = self.action.old_value
        # In auth action IDENTITY_OWNER is a '', but in accepted_roles it's None
        self.role = self.role if self.role != '' else None
        self.role_string = roles_to_string[self.role]
        self.role_to_change = self.action.new_value
        self.role_to_change = self.role_to_change if self.role_to_change != '' else None
        self.role_to_change_string = roles_to_string[self.role_to_change]
        self.need_to_be_owner = constraint.need_to_be_owner if hasattr(constraint, 'need_to_be_owner') else False
        self.other_roles = []
        self.default_who_can_wallet = None
        self.new_who_can_wallet = None
        self.new_default_did = None
        self.add_new_role_cls = add_new_role_cls

    def prepare(self):
        default_constraint_roles = []
        self.get_default_roles(self.constraint, default_constraint_roles)
        default_role = random.choice(default_constraint_roles)
        default_role = default_role if default_role != '*' else self.role
        self.other_roles = set(accepted_roles).difference(set(default_constraint_roles).union({'*', default_role}))
        self.new_default_did = self.create_role()
        if self.need_to_be_owner:
            self.default_who_can_wallet = (self.trustee_wallet[0], self.new_default_did)
        else:
            self.default_who_can_wallet = self.env.role_to_wallet[default_role]
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

        self.default_edit_nym_1 = self._get_default_edit_nym()
        self.default_edit_nym_2 = self._get_default_edit_nym()
        self.nym_for_new_rule = self._get_nym_for_new_rule()

        self.return_to_default_nym_1 = self._return_to_default_nym()
        self.return_to_default_nym_2 = self._return_to_default_nym()
        self.return_to_nym_for_new_rule = self._return_to_default_nym()

    def run(self):

        # Step 1. Change AUTH_RULE
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot edit nym in default way
        with pytest.raises(RequestRejectedException):
            self.send_and_check(self.default_edit_nym_1, wallet=self.default_who_can_wallet)

        # Step 3. Check, that new auth rule worked
        self.send_and_check(self.nym_for_new_rule, wallet=self.new_who_can_wallet)

        # Step 4. Return to default role
        if self.role != self.role_to_change:
            self.send_and_check(self.return_to_nym_for_new_rule, wallet=self.trustee_wallet)

        # Step 5. Return back to default auth rules
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 6. Check, that now we can editing
        self.send_and_check(self.default_edit_nym_2, wallet=self.default_who_can_wallet)

        # Step 7. Return to default value
        if self.role != self.role_to_change:
            self.send_and_check(self.return_to_default_nym_2, wallet=self.trustee_wallet)

    def result(self):
        pass

    def get_default_roles(self, constraint, d_roles):
        if constraint.constraint_id != ConstraintsEnum.ROLE_CONSTRAINT_ID:
            for a_c in constraint.auth_constraints:
                self.get_default_roles(a_c, d_roles)
        else:
            d_roles.append(constraint.role)
        return d_roles

    def create_role(self):
        add_new_role = self.add_new_role_cls(self.env)
        new_role_nym = add_new_role.get_nym()
        res = add_new_role.send_and_check(new_role_nym, wallet=self.trustee_wallet)
        new_did = res[1]['result']['txn']['data']['dest']
        return new_did

    def _get_nym_for_new_rule(self):
        return self._build_nym(self.new_who_can_wallet,
                               self.role_to_change_string,
                               self.new_default_did)

    def _get_default_edit_nym(self):
        return self._build_nym(self.default_who_can_wallet,
                               self.role_to_change_string,
                               self.new_default_did)

    def _return_to_default_nym(self):
        return self._build_nym(self.trustee_wallet,
                               self.role_string,
                               self.new_default_did)

    def get_changed_auth_rule(self):
        new_role = random.choice(list(self.other_roles))
        self.new_who_can_wallet = self.env.role_to_wallet[new_role]
        constraint = AuthConstraint(role=new_role,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=self.action.prefix,
            auth_type=self.action.txn_type,
            field=self.action.field,
            old_value=self.action.old_value,
            new_value=self.action.new_value,
            constraint=constraint.as_dict
        )


class EditTrusteeToStewardTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewTrusteeTest)


class EditTrusteeToEndorserTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewTrusteeTest)


class EditTrusteeToNetworkMonitorTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewTrusteeTest)


class EditTrusteeToIdentityOwnerTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewTrusteeTest)


class EditStewardToTrusteeTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewStewardTest)


class EditStewardToNetworkMonitorTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewStewardTest)


class EditStewardToEndorserTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewStewardTest)


class EditStewardToIdentityOwnerTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewStewardTest)


class EditEndorserToTrusteeTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewEndorserTest)


class EditEndorserToStewardTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewEndorserTest)


class EditEndorserToNetworkMonitorTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewEndorserTest)


class EditEndorserToIdentityOwnerTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewEndorserTest)


class EditIdentityOwnerToTrusteeTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewIdentityOwnerTest)


class EditIdentityOwnerToStewardTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewIdentityOwnerTest)


class EditIdentityOwnerToEndorserTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewIdentityOwnerTest)


class EditIdentityOwnerToNetworkMonitorTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewIdentityOwnerTest)


class EditNetworkMonitorToTrusteeTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewNetworkMonitorTest)


class EditNetworkMonitorToStewardTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewNetworkMonitorTest)


class EditNetworkMonitorToEndorserTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewNetworkMonitorTest)


class EditNetworkMonitorToIdentityOwnerTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewNetworkMonitorTest)


class EditStewardToStewardTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewStewardTest)


class EditTrusteeToTrusteeTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewTrusteeTest)


class EditEndorserToEndorserTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewEndorserTest)


class EditNetworkMonitorToNetworkMonitorTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewNetworkMonitorTest)


class EditIdentityOwnerToIdentityOwnerTest(EditRoleTest):
    def __init__(self, env, action_id):
        super().__init__(action_id,
                         env,
                         AddNewIdentityOwnerTest)
