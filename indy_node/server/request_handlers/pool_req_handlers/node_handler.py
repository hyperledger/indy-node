from copy import deepcopy

from indy_common.constants import NODE

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.common.constants import DATA, SERVICES, VALIDATOR, TARGET_NYM, ALIAS, BLS_KEY_PROOF
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.node_handler import NodeHandler as PNodeHandler


class NodeHandler(PNodeHandler):

    def __init__(self, database_manager: DatabaseManager, bls_crypto_verifier,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, bls_crypto_verifier)
        self.write_req_validator = write_req_validator

    def _is_steward(self, nym, is_committed: bool = True):
        return self.database_manager.idr_cache.hasSteward(nym, is_committed)

    def _get_node_data(self, nym, is_committed: bool = True):
        key = nym.encode()
        data = self.state.get(key, is_committed)
        if not data:
            return {}
        return self.state_serializer.deserialize(data)

    def _auth_error_while_adding_node(self, request):
        origin = request.identifier
        operation = request.operation
        data = operation.get(DATA, {})
        error = self._data_error_while_validating(data, skip_keys=False)
        if error:
            return error

        if self._steward_has_node(origin):
            return "{} already has a node".format(origin)
        error = self._is_node_data_conflicting(data)
        if error:
            return "existing data has conflicts with " \
                   "request data {}. Error: {}".format(operation.get(DATA), error)
        self.write_req_validator.validate(request,
                                          [AuthActionAdd(txn_type=NODE,
                                                         field=SERVICES,
                                                         value=data.get(SERVICES, [VALIDATOR]))])

    def _auth_error_while_updating_node(self, request):
        origin = request.identifier
        is_trustee = self.database_manager.idr_cache.hasTrustee(origin, isCommitted=False)
        if not is_trustee:
            error = super()._auth_error_while_updating_node(request)
            if error:
                return error
        origin = request.identifier
        operation = request.operation
        node_nym = operation.get(TARGET_NYM)

        data = operation.get(DATA, {})
        error = self._data_error_while_validating_update(data, node_nym)
        if error:
            return error

        is_steward_of_node = self._is_steward_of_node(
            origin, node_nym, is_committed=False)

        node_info = self.get_from_state(node_nym, is_committed=False)
        data = deepcopy(data)
        data.pop(ALIAS, None)
        for k in data:
            if k == BLS_KEY_PROOF:
                continue
            old_val = node_info.get(k, None) if node_info else None
            new_val = data[k]
            if k == SERVICES:
                if not old_val:
                    old_val = []
                if not new_val:
                    new_val = []
            if old_val != new_val:
                self.write_req_validator.validate(request,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=k,
                                                                  old_value=old_val,
                                                                  new_value=new_val,
                                                                  is_owner=is_steward_of_node)])
