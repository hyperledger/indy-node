from collections import OrderedDict

import rlp
from plenum.common.constants import VERKEY, TRUSTEE, STEWARD
from plenum.common.types import f
from sovrin_common.constants import ROLE, TGB, TRUST_ANCHOR
from state.kv.kv_store import KeyValueStorage
from stp_core.common.log import getlogger

logger = getlogger()


class IdrCache:
    """
    A cache to store a role and verkey of an identifier, the db is only used to
    store committed data, uncommitted data goes to memory
    The key is the identifier and value is a pack of fields in rlp
    The first item is the trust anchor, the second item is verkey and the
    third item is role
    """

    unsetVerkey = b'-'

    def __init__(self, name, keyValueStorage: KeyValueStorage):
        logger.debug('Initializing identity cache {}'.format(name))
        self._keyValueStorage = keyValueStorage
        self._name = name
        # List of Tuples where first items is the state root after batch and
        # second item is a dictionary similar to cache which can be queried
        # like the database, i.e `self._db`. Keys (state roots are purged)
        # when they get committed or reverted.
        self.unCommitted = [] # type: List[Tuple[bytes, OrderedDict]]

        # Relevant NYMs operation done in current batch, in order
        self.currentBatchOps = []   # type: List[Tuple]

    def __repr__(self):
        return self._name

    @staticmethod
    def encodeVerkey(verkey):
        if verkey is None:
            return IdrCache.unsetVerkey
        else:
            if isinstance(verkey, str):
                return verkey.encode()
            return verkey

    @staticmethod
    def decodeVerkey(verkey):
        if verkey == IdrCache.unsetVerkey:
            return None
        else:
            return verkey.decode()

    @staticmethod
    def packIdrValue(ta=None, role=None, verkey=None):
        if ta is None:
            ta = b''
        if role is None:
            role = b''
        verkey = IdrCache.encodeVerkey(verkey)
        return rlp.encode([ta, verkey, role])

    @staticmethod
    def unpackIdrValue(value):
        ta, verkey, role = rlp.decode(value)
        return ta.decode(), IdrCache.decodeVerkey(verkey), role.decode()

    def get(self, idr, isCommitted=True):
        idr = idr.encode()
        if isCommitted:
            value = self._keyValueStorage.get(idr)
        else:
            # Looking for uncommitted values, iterating over `self.unCommitted`
            # in reverse to get the latest value
            for _, cache in reversed(self.unCommitted):
                if idr in cache:
                    value = cache[idr]
                    break
            else:
                value = self._keyValueStorage.get(idr)
        ta, iv, r = self.unpackIdrValue(value)
        return ta, iv, r

    def set(self, idr, ta=None, verkey=None, role=None, isCommitted=True):
        val = self.packIdrValue(ta, role, verkey)
        if isCommitted:
            self._keyValueStorage.put(idr, val)
        else:
            self.currentBatchOps.append((idr, val))

    def close(self):
        self._keyValueStorage.close()

    def currentBatchCreated(self, stateRoot):
        self.unCommitted.append((stateRoot, OrderedDict(self.currentBatchOps)))
        self.currentBatchOps = []

    def batchRejected(self):
        # Batches are always rejected from end of `self.unCommitted`
        self.currentBatchOps = []
        self.unCommitted = self.unCommitted[:-1]

    def onBatchCommitted(self, stateRoot):
        # Commit an already created batch
        if self.unCommitted:
            assert self.unCommitted[0][0] == stateRoot, 'The first created batch has ' \
                                                     'not been committed or ' \
                                                     'reverted and yet another ' \
                                                     'batch is trying to be ' \
                                                     'committed, {} {}'.format(
                self.unCommitted[0][0], stateRoot)
            self._keyValueStorage.setBatch([(idr, val) for idr, val in
                                            self.unCommitted[0][1].items()])
            self.unCommitted = self.unCommitted[1:]
        else:
            logger.warning('{} is trying to commit a batch with state root {} '
                           'but no uncommitted found'.format(self, stateRoot))

    def setVerkey(self, idr, verkey):
        # This method acts as if guardianship is being terminated.
        _, _, role = self.get(idr)
        self.set(idr, ta=None, verkey=verkey, role=role)

    def setRole(self, idr, role):
        ta, v, _ = self.get(idr)
        self.set(idr, ta=ta, verkey=v, role=role)

    def getVerkey(self, idr, isCommitted=True):
        _, v, _ = self.get(idr, isCommitted=isCommitted)
        return v

    def getRole(self, idr, isCommitted=True):
        _, _, role = self.get(idr, isCommitted=isCommitted)
        return role

    def getNym(self, nym, role=None, isCommitted=True):
        """
        Get a nym, if role is provided then get nym with that role
        :param nym:
        :param role:
        :param isCommitted:
        :return:
        """
        try:
            ta, verkey, r = self.get(nym, isCommitted)
        except KeyError:
            return None
        if role and role != r:
            return None
        return {
            ROLE: r,
            VERKEY: verkey,
            f.IDENTIFIER.nm: ta if ta else None
        }

    def getTrustee(self, nym, isCommitted=True):
        return self.getNym(nym, TRUSTEE, isCommitted=isCommitted)

    def getTGB(self, nym, isCommitted=True):
        return self.getNym(nym, TGB, isCommitted=isCommitted)

    def getSteward(self, nym, isCommitted=True):
        return self.getNym(nym, STEWARD, isCommitted=isCommitted)

    def getTrustAnchor(self, nym, isCommitted=True):
        return self.getNym(nym, TRUST_ANCHOR, isCommitted=isCommitted)

    def hasTrustee(self, nym, isCommitted=True):
        return bool(self.getTrustee(nym, isCommitted=isCommitted))

    def hasTGB(self, nym, isCommitted=True):
        return bool(self.getTGB(nym, isCommitted=isCommitted))

    def hasSteward(self, nym, isCommitted=True):
        return bool(self.getSteward(nym, isCommitted=isCommitted))

    def hasTrustAnchor(self, nym, isCommitted=True):
        return bool(self.getTrustAnchor(nym, isCommitted=isCommitted))

    def hasNym(self, nym, isCommitted=True):
        return bool(self.getNym(nym, isCommitted=isCommitted))

    def getOwnerFor(self, nym, isCommitted=True):
        nymData = self.getNym(nym, isCommitted=isCommitted)
        if nymData:
            if nymData.get(VERKEY) is None:
                return nymData[f.IDENTIFIER.nm]
            else:
                return nym
        logger.error('Nym {} not found'.format(nym))
