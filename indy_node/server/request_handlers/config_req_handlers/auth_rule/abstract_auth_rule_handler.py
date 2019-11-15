from abc import ABCMeta

from common.serializers.serialization import domain_state_serializer, config_state_serializer
from indy_common.authorize.auth_constraints import ConstraintCreator, ConstraintsSerializer, OFF_LEDGER_SIGNATURE, \
    CONSTRAINT_ID, ConstraintsEnum, AUTH_CONSTRAINTS
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from indy_common.constants import CONFIG_LEDGER_ID, CONSTRAINT
from indy_common.state.state_constants import MARKER_AUTH_RULE
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.exceptions import InvalidClientRequest
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class AbstractAuthRuleHandler(WriteRequestHandler, metaclass=ABCMeta):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator, txn_type):
        super().__init__(database_manager, txn_type, CONFIG_LEDGER_ID)
        self.write_req_validator = write_req_validator
        self.constraint_serializer = ConstraintsSerializer(domain_state_serializer)
        self.config = getConfig()
        self._update_state_by_versions = self._get_update_state_by_versions()

    def _static_validation_for_rule(self, operation, identifier, req_id):
        try:
            ConstraintCreator.create_constraint(operation.get(CONSTRAINT))
        except (ValueError, KeyError) as exp:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       exp)
        StaticAuthRuleHelper.check_auth_key(operation, identifier, req_id, self.write_req_validator.auth_map)

    def _update_auth_constraint(self, auth_key: str, constraint):
        version = self.database_manager.state_version
        if version in self._update_state_by_versions:
            self._update_state_by_versions[version](auth_key, constraint)
        else:
            self.state.set(AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key),
                           self.constraint_serializer.serialize(constraint))

    def _update_auth_constraint_for_1_9_1(self, auth_key: str, constraint):
        constraint_dict = constraint.as_dict if constraint else {}
        self._set_off_ledger_to_constraint(constraint_dict)
        self.state.set(AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key),
                       self.constraint_serializer.serializer.serialize(constraint_dict))

    def _set_off_ledger_to_constraint(self, constraint_dict):
        if constraint_dict[CONSTRAINT_ID] == ConstraintsEnum.ROLE_CONSTRAINT_ID:
            constraint_dict[OFF_LEDGER_SIGNATURE] = None
        for constraint in constraint_dict.get(AUTH_CONSTRAINTS, []):
            self._set_off_ledger_to_constraint(constraint)

    def _decode_state_value(self, encoded):
        if encoded:
            return config_state_serializer.deserialize(encoded)
        return None

    @staticmethod
    def make_state_path_for_auth_rule(action_id) -> bytes:
        return "{MARKER}:{ACTION_ID}" \
            .format(MARKER=MARKER_AUTH_RULE,
                    ACTION_ID=action_id).encode()

    def _get_update_state_by_versions(self):
        update_state_functions = {"1.9.1": self._update_auth_constraint_for_1_9_1}
        for node_version, other_version in self.config.INDY_NODE_VERSION_MATCHING.items():
            # TODO: change `_update_state_by_versions` keys format
            # because indy-node and other packets can have same version
            if node_version in update_state_functions:
                update_state_functions[other_version] = update_state_functions.pop(node_version)
        return update_state_functions
