import os

from collections import OrderedDict
import rlp

from plenum.common.constants import VERKEY, TRUSTEE, STEWARD, GUARDIAN
from plenum.common.types import f
from plenum.persistence.kv_store_leveldb import KVStoreLeveldb
from sovrin_common.constants import ROLE, TGB, TRUST_ANCHOR
from stp_core.common.log import getlogger

logger = getlogger()


class IdrCache:
    """
    A cache to store a role and verkey of an identifier, the db is only used to
    store committed data, uncommitted data goes to memory
    The key is the identifier and value is a pack of fields
    The first byte indicates whether the identifier has a guardian or not,
    if it has then the next few bytes will be the guardian's identifier
    otherwise they will be the verkey. Then there is delimiter byte after which
    the value of role starts. eg.
    Value in case of guardian: '\2<guardian's DID>\0<role of the DID>'
    Value in case of no guardian: '\1<verkey of the DID>\0<role of the DID>'
    """

    unsetVerkey = b'-'

    def __init__(self, basedir: str, name):
        logger.debug('Initializing identity cache {} at {}'
                     .format(name, basedir))
        self._basedir = basedir
        self._name = name
        self._db = None
        self.open()
        # OrderedDict where key is the state root after batch and value is a
        # dictionary similar to cache which can be queried like the
        # database, i.e `self._db`. Keys (state roots are purged) when they
        # get committed or reverted.
        self.unCommitted = OrderedDict() # type: Dict[bytes, OrderedDict]

        # Relevant NYMs operation done in current batch, in order
        self.currentBatchOps = []   # type: List[Tuple]

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
    def getPrefixAndIv(guardian=None, verkey=None):
        iv = guardian if guardian else verkey
        prefix = b'1' if guardian else b'0'
        return prefix, iv

    @staticmethod
    def packIdrValue(ta=None, role=None, verkey=None):
        # prefix, iv = IdrCache.getPrefixAndIv(guardian, verkey)
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
            value = self._db.get(idr)
        else:
            # Looking for uncommitted values, iterating over `self.unCommitted`
            # in reverse to get the latest value
            for i, cache in reversed(self.unCommitted.items()):
                if idr in cache:
                    value = cache[idr]
                    break
            else:
                value = self._db.get(idr)
        ta, iv, r = self.unpackIdrValue(value)
        return ta, iv, r

    def set(self, idr, ta=None, verkey=None, role=None, isCommitted=True):
        val = self.packIdrValue(ta, role, verkey)
        if isCommitted:
            self._db.set(idr, val)
        else:
            self.currentBatchOps.append((idr, val))

    def close(self):
        self._db.close()

    def open(self):
        self._db = KVStoreLeveldb(self.dbPath)

    @property
    def dbPath(self):
        return os.path.join(self._basedir, self._name)

    def currentBatchCreated(self, stateRoot):
        self.unCommitted[stateRoot] = OrderedDict(self.currentBatchOps)
        self.currentBatchOps = []

    def batchRejected(self, stateRoot=None):
        if stateRoot:
            self.unCommitted[stateRoot] = OrderedDict(self.currentBatchOps)
        else:
            self.currentBatchOps = []

    def onBatchCommitted(self, stateRoot):
        self._db.setBatch([(idr, val) for idr, val in self.unCommitted[stateRoot].items()])
        self.unCommitted.pop(stateRoot)

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
