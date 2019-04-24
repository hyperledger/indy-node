import random

from indy_common.authorize.auth_actions import split_action_id
from indy_common.authorize.auth_constraints import AbstractAuthConstraint, accepted_roles, ConstraintsEnum, \
    AuthConstraint
from indy_common.constants import NETWORK_MONITOR
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, roles_to_string
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from plenum.test.helper import sdk_gen_request


class EditTrusteeTest(AbstractTest):
    def __init__(self, action_id: str, constraint: AbstractAuthConstraint, env):
        self.action_id = action_id
        self.action = split_action_id(action_id)
        self.constraint = constraint
        self.env = env
        self.role = self.action.new_value
        self.role_string = roles_to_string[self.role]
        self.trustee_wallet = env.sdk_wallet_trustee
        self.default_constraint_roles = []
        self.other_roles = []
        self.checker_wallet = None
        self.default_wallet = None
        self.new_default_did = None
        self.role_to_change = None

    def prepare(self):
        self.default_constraint_roles = self.get_default_roles(self.constraint)
        self.other_roles = set(accepted_roles).difference(set(self.default_constraint_roles).union({NETWORK_MONITOR}))
        self.new_default_did = self.create_role()
        self.default_edit_nym = self._get_default_edit_nym()
        self.return_to_default_nym = self._return_to_default_nym()
        self.default_auth_rule = self.get_default_auth_rule()



    def get_default_roles(self, constraint):
        d_roles = []
        if constraint.constraint_id != ConstraintsEnum.ROLE_CONSTRAINT_ID:
            for a_c in constraint.auth_constraints:
                self.get_default_roles(a_c)
        d_roles.append(constraint.role)
        return d_roles

    def create_role(self):
        add_new_trustee = AddNewTrusteeTest(self.env)
        new_trustee_nym = add_new_trustee.get_nym()
        return add_new_trustee.send_and_check(new_trustee_nym)

    def _get_default_edit_nym(self):
        return self._build_nym(self.default_wallet,
                               roles_to_string[random.choice(set(accepted_roles).difference(self.role))],
                               self.new_default_did)

    def _return_to_default_nym(self):
        return self._build_nym(self.default_wallet,
                               self.role_string,
                               self.new_default_did)

    def get_changed_auth_rule(self):
        new_role = random.choice(set(accepted_roles).difference(set(self.other_roles)))
        self.checker_wallet = self.env.role_to_wallet[new_role]
        self.role_to_change = new_role
        constraint = AuthConstraint(role=new_role,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=self.action_def.prefix,
                                                 auth_type=self.action_def.txn_type,
                                                 field=self.action_def.field,
                                                 old_value=self.action_def.old_value,
                                                 new_value=self.action_def.new_value,
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])