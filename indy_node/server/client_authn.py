from copy import deepcopy
from hashlib import sha256

from plenum.common.types import OPERATION
from plenum.common.constants import TXN_TYPE, RAW, ENC, HASH
from plenum.server.client_authn import NaclAuthNr, CoreAuthNr, CoreAuthMixin

from indy_common.constants import ATTRIB, POOL_UPGRADE, SCHEMA, CLAIM_DEF, \
    GET_NYM, GET_ATTR, GET_SCHEMA, GET_CLAIM_DEF, POOL_CONFIG, POOL_RESTART, \
    REVOC_REG_DEF, REVOC_REG_ENTRY, \
    GET_REVOC_REG_DEF, GET_REVOC_REG, GET_REVOC_REG_DELTA, VALIDATOR_INFO, AUTH_RULE, GET_AUTH_RULE
from indy_node.persistence.idr_cache import IdrCache


class LedgerBasedAuthNr(CoreAuthMixin, NaclAuthNr):
    """
    Transaction-based client authenticator.
    """

    write_types = CoreAuthMixin.write_types.union({ATTRIB, SCHEMA, CLAIM_DEF,
                                                   POOL_CONFIG, POOL_UPGRADE, AUTH_RULE,
                                                   REVOC_REG_DEF, REVOC_REG_ENTRY})
    query_types = CoreAuthMixin.query_types.union({GET_NYM, GET_ATTR, GET_SCHEMA,
                                                   GET_CLAIM_DEF, GET_REVOC_REG_DEF,
                                                   GET_REVOC_REG, GET_REVOC_REG_DELTA,
                                                   GET_AUTH_RULE})
    action_types = CoreAuthMixin.action_types.union({POOL_RESTART, VALIDATOR_INFO})

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
