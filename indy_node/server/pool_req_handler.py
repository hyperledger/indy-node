import ctypes
from copy import deepcopy

import base58
from libnacl import nacl, crypto_box_PUBLICKEYBYTES

from common.serializers.serialization import pool_state_serializer
from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from plenum.common.constants import TARGET_NYM, DATA, ALIAS, SERVICES, \
    BLS_KEY_PROOF, VALIDATOR, VERKEY

from plenum.common.ledger import Ledger
from plenum.server.pool_req_handler import PoolRequestHandler as PHandler
from indy_common.constants import NODE
from indy_node.persistence.idr_cache import IdrCache
from state.state import State
from stp_core.crypto.util import ed25519PkToCurve25519


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

        dest = operation.get(TARGET_NYM)
        if not self.base58_is_correct_ed25519_key(dest):
            return "Node's dest is not correct Ed25519 key. Dest: {}".format(dest)

        verkey = operation.get(VERKEY, None)
        if verkey:
            if not self.base58_is_correct_ed25519_key(verkey):
                return "Node's verkey is not correct Ed25519 key. Verkey: {}".format(verkey)

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

        verkey = operation.get(VERKEY, None)
        if verkey:
            if not self.base58_is_correct_ed25519_key(verkey):
                return "Node's verkey is not correct Ed25519 key. Verkey: {}".format(verkey)

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

    @staticmethod
    def base58_is_correct_ed25519_key(key):
        try:
            ed25519PkToCurve25519(base58.b58decode(key))
        except Exception:
            return False
        return True
