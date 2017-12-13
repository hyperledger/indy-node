from copy import deepcopy
from hashlib import sha256

from indy_node.server.config_req_handler import ConfigReqHandler
from plenum.common.types import OPERATION
from plenum.common.constants import TXN_TYPE, RAW, ENC, HASH
from plenum.server.client_authn import NaclAuthNr, CoreAuthNr, CoreAuthMixin

from indy_common.constants import ATTRIB, GET_TXNS
from indy_node.server.pool_req_handler import PoolRequestHandler
from indy_node.server.domain_req_handler import DomainReqHandler

from indy_node.persistence.idr_cache import IdrCache


class LedgerBasedAuthNr(CoreAuthMixin, NaclAuthNr):
    """
    Transaction-based client authenticator.
    """

    write_types = CoreAuthMixin.write_types.union(
        PoolRequestHandler.write_types
    ).union(
        DomainReqHandler.write_types
    ).union(
        ConfigReqHandler.write_types
    )

    query_types = CoreAuthMixin.query_types.union(
        {GET_TXNS, }
    ).union(
        PoolRequestHandler.query_types
    ).union(
        DomainReqHandler.query_types
    ).union(
        ConfigReqHandler.query_types
    )

    def __init__(self, cache: IdrCache):
        NaclAuthNr.__init__(self)
        CoreAuthMixin.__init__(self)
        self.cache = cache

    def serializeForSig(self, msg, identifier=None, topLevelKeysToIgnore=None):
        if msg[OPERATION].get(TXN_TYPE) == ATTRIB:
            msgCopy = deepcopy(msg)
            keyName = {RAW, ENC, HASH}.intersection(
                set(msgCopy[OPERATION].keys())).pop()
            msgCopy[OPERATION][keyName] = sha256(
                msgCopy[OPERATION][keyName].encode()).hexdigest()
            return super().serializeForSig(msgCopy, identifier=identifier,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)
        else:
            return super().serializeForSig(msg, identifier=identifier,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)

    def addIdr(self, identifier, verkey, role=None):
        raise RuntimeError('Add verification keys through the NYM txn')

    def getVerkey(self, identifier):
        try:
            verkey = self.cache.getVerkey(identifier, isCommitted=False)
        except KeyError:
            return None
        return verkey
