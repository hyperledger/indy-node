from copy import deepcopy

from plenum.common.txn import POOL_TXN_TYPES, TXN_TYPE, DATA, ALIAS, \
    TARGET_NYM
from plenum.server.pool_manager import HasPoolManager as PHasPoolManager, \
    TxnPoolManager as PTxnPoolManager
from sovrin_common.auth import Authoriser


class HasPoolManager(PHasPoolManager):
    # noinspection PyUnresolvedReferences, PyTypeChecker
    def __init__(self, nodeRegistry=None, ha=None, cliname=None, cliha=None):
        if not nodeRegistry:
            self.poolManager = TxnPoolManager(self, ha=ha, cliname=cliname,
                                              cliha=cliha)
            for types in POOL_TXN_TYPES:
                self.requestExecuter[types] = \
                    self.poolManager.executePoolTxnRequest
        else:
            super().__init__(nodeRegistry=nodeRegistry, ha=ha, cliname=cliname,
                             cliha=cliha)


class TxnPoolManager(PTxnPoolManager):
    def authErrorWhileUpdatingNode(self, request):
        origin = request.identifier
        isTrustee = self.node.secondaryStorage.isTrustee(origin)
        if not isTrustee:
            error = super().authErrorWhileUpdatingNode(request)
            if error:
                return error
        origin = request.identifier
        operation = request.operation
        nodeNym = operation.get(TARGET_NYM)
        isSteward = self.node.secondaryStorage.isSteward(origin)
        actorRole = self.node.graphStore.getRole(origin)
        _, nodeInfo = self.getNodeInfoFromLedger(nodeNym, excludeLast=False)
        typ = operation.get(TXN_TYPE)
        data = deepcopy(operation.get(DATA))
        data.pop(ALIAS, None)
        vals = []
        msgs = []
        for k in data:
            oldVal = nodeInfo[DATA][k]
            newVal = data[k]
            if oldVal != newVal:
                r, msg = Authoriser.authorised(typ, k, actorRole,
                                           oldVal=oldVal,
                                           newVal=newVal,
                                           isActorOwnerOfSubject=isSteward)
                vals.append(r)
                msgs.append(msg)
        msg = None if all(vals) else '\n'.join(msgs)
        return msg
