from copy import deepcopy

from common.serializers.serialization import pool_state_serializer
from plenum.common.constants import TARGET_NYM, DATA, ALIAS, SERVICES

from plenum.common.ledger import Ledger
from plenum.server.pool_req_handler import PoolRequestHandler as PHandler
from indy_common.auth import Authoriser
from indy_common.constants import NODE
from indy_node.persistence.idr_cache import IdrCache
from state.state import State


class PoolRequestHandler(PHandler):
    def __init__(self, ledger: Ledger, state: State,
                 domainState: State, idrCache: IdrCache):
        super().__init__(ledger, state, domainState)
        self.stateSerializer = pool_state_serializer
        self.idrCache = idrCache

    def isSteward(self, nym, isCommitted: bool=True):
        return self.idrCache.hasSteward(nym, isCommitted)

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

        actorRole = self.idrCache.getRole(origin, isCommitted=False)
        nodeInfo = self.getNodeData(nodeNym, isCommitted=False)
        data = deepcopy(data)
        data.pop(ALIAS, None)
        vals = []
        msgs = []
        for k in data:
            oldVal = nodeInfo.get(k, None) if nodeInfo else None
            newVal = data[k]
            if k == SERVICES:
                if not oldVal:
                    oldVal = []
                if not newVal:
                    newVal = []
            if oldVal != newVal:
                r, msg = Authoriser.authorised(NODE, actorRole,
                                               field=k,
                                               oldVal=oldVal,
                                               newVal=newVal,
                                               isActorOwnerOfSubject=isStewardOfNode)
                vals.append(r)
                msgs.append(msg)
        msg = None if all(vals) else '\n'.join(msgs)
        return msg
