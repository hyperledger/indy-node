from copy import deepcopy

from common.serializers.serialization import pool_state_serializer
from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from plenum.common.constants import TARGET_NYM, DATA, ALIAS, SERVICES, \
    BLS_KEY_PROOF, VALIDATOR

from plenum.common.ledger import Ledger
from plenum.server.pool_req_handler import PoolRequestHandler as PHandler
from indy_common.constants import NODE
from indy_node.persistence.idr_cache import IdrCache
from state.state import State


class PoolRequestHandler(PHandler):
    def __init__(self, ledger: Ledger, state: State,
                 states, idrCache: IdrCache, write_req_validator):
        super().__init__(ledger, state, states)
        self.stateSerializer = pool_state_serializer
        self.idrCache = idrCache
        self.write_req_validator = write_req_validator

    def isSteward(self, nym, isCommitted: bool = True):
        return self.idrCache.hasSteward(nym, isCommitted)

    def authErrorWhileAddingNode(self, request):
        origin = request.identifier
        operation = request.operation
        data = operation.get(DATA, {})
        error = self.dataErrorWhileValidating(data, skipKeys=False)
        if error:
            return error

        if self.stewardHasNode(origin):
            return "{} already has a node".format(origin)
        error = self.isNodeDataConflicting(data)
        if error:
            return "existing data has conflicts with " \
                   "request data {}. Error: {}".format(operation.get(DATA), error)
        self.write_req_validator.validate(request,
                                          [AuthActionAdd(txn_type=NODE,
                                                         field=SERVICES,
                                                         value=data.get(SERVICES, [VALIDATOR]))])

    def authErrorWhileUpdatingNode(self, request):
        origin = request.identifier
        isTrustee = self.idrCache.hasTrustee(origin, isCommitted=False)
        if not isTrustee:
            error = super().authErrorWhileUpdatingNode(request)
            if error:
                return error
        origin = request.identifier
        operation = request.operation
        nodeNym = operation.get(TARGET_NYM)

        data = operation.get(DATA, {})
        error = self.dataErrorWhileValidatingUpdate(data, nodeNym)
        if error:
            return error

        isStewardOfNode = self.isStewardOfNode(
            origin, nodeNym, isCommitted=False)

        nodeInfo = self.getNodeData(nodeNym, isCommitted=False)
        data = deepcopy(data)
        data.pop(ALIAS, None)
        for k in data:
            if k == BLS_KEY_PROOF:
                continue
            oldVal = nodeInfo.get(k, None) if nodeInfo else None
            newVal = data[k]
            if k == SERVICES:
                if not oldVal:
                    oldVal = []
                if not newVal:
                    newVal = []
            if oldVal != newVal:
                self.write_req_validator.validate(request,
                                                  [AuthActionEdit(txn_type=NODE,
                                                                  field=k,
                                                                  old_value=oldVal,
                                                                  new_value=newVal,
                                                                  is_owner=isStewardOfNode)])
