from copy import deepcopy
from hashlib import sha256

from plenum.common.types import OPERATION
from plenum.common.constants import TXN_TYPE, RAW, ENC, HASH, NYM
from plenum.server.client_authn import NaclAuthNr, CoreAuthMixin

from indy_common.constants import ATTRIB
from indy_node.persistence.idr_cache import IdrCache
from plenum.server.request_handlers.utils import get_request_type, nym_ident_is_dest, get_target_verkey


class LedgerBasedAuthNr(CoreAuthMixin, NaclAuthNr):
    """
    Transaction-based client authenticator.
    """

    def __init__(self, write_types, query_types, action_types, cache: IdrCache):
        NaclAuthNr.__init__(self)
        CoreAuthMixin.__init__(self, write_types, query_types, action_types)
        self.cache = cache
        self.specific_verkey_validation = {NYM: self.nym_specific_auth}

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

    def getVerkey(self, ident, request):
        try:
            verkey = self.cache.getVerkey(ident, isCommitted=False)
        except KeyError:
            # If DID wasn't found in idr cache, then it can be
            # creation of a new DID signed by a verkey for this new DID
            verkey = self.get_verkey_specific(request)
            if not verkey:
                return None
            else:
                return verkey
        return verkey

    def get_verkey_specific(self, request):
        typ = get_request_type(request)
        verkey_validation = self.specific_verkey_validation.get(typ)
        if verkey_validation is None:
            return None
        verkey = verkey_validation(request)
        return verkey

    def nym_specific_auth(self, request):
        # As far as we allow non-ledger nyms send their own txn,
        # we need to check if it's target verkey is correct
        if nym_ident_is_dest(request):
            return get_target_verkey(request)
        else:
            return None
