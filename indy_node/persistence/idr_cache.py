from collections import OrderedDict
import rlp
from plenum.common.constants import VERKEY, TRUSTEE, STEWARD, THREE_PC_PREFIX, \
    TXN_TIME
from plenum.common.types import f
from storage.kv_store import KeyValueStorage

from indy_common.constants import ROLE, TGB, TRUST_ANCHOR
from stp_core.common.log import getlogger

logger = getlogger()


# TODO: consider removing IdrCache in favour of some wrapper over state
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
        self.unCommitted = []  # type: List[Tuple[bytes, OrderedDict]]

        # Relevant NYMs operation done in current batch, in order
        self.currentBatchOps = []   # type: List[Tuple]

    def __repr__(self):
        return self._name

    @staticmethod
    def encodeVerkey(verkey):
        if verkey is None:
            return IdrCache.unsetVerkey
        if isinstance(verkey, str):
            return verkey.encode()
        return verkey

    @staticmethod
    def decodeVerkey(verkey):
        if verkey != IdrCache.unsetVerkey:
            return verkey.decode()

    @staticmethod
    def packIdrValue(seqNo, txnTime, ta, role, verkey):
        if seqNo is None:
            raise ValueError("seqNo should not be None!")
        seqNo = str(seqNo)
        txnTime = b'' if txnTime is None else str(txnTime)
        if ta is None:
            ta = b''
        if role is None:
            role = b''
        verkey = IdrCache.encodeVerkey(verkey)
        return rlp.encode([seqNo, txnTime, ta, role, verkey])

    @staticmethod
    def unpackIdrValue(value):
        if value is None:
            return None
        seqNo, txnTime, ta, role, verkey = rlp.decode(value)
        seqNo = int(seqNo.decode())
        txnTime = txnTime.decode()
        txnTime = int(txnTime) if txnTime else None
        ta = ta.decode()
        role = role.decode()
        verkey = IdrCache.decodeVerkey(verkey)
        return seqNo, txnTime, ta, role, verkey

    def get(self, idr, isCommitted=True):
        encoded_idr = idr.encode()
        if not isCommitted:
            # Looking for uncommitted values,
            # iterating over `currentBatchOps and unCommitted`
            # in reverse to get the latest value
            for key, cache in reversed(self.currentBatchOps):
                if key == idr:
                    return self.unpackIdrValue(cache)
            for _, cache in reversed(self.unCommitted):
                if encoded_idr in cache:
                    return self.unpackIdrValue(cache[encoded_idr])
        value = self._keyValueStorage.get(encoded_idr)
        return self.unpackIdrValue(value)

    def set(self, idr, seqNo, txnTime, ta=None, role=None, verkey=None, isCommitted=True):
        val = self.packIdrValue(seqNo, txnTime, ta, role, verkey)
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
        if not self.unCommitted:
            logger.warning('{}{} is trying to commit a batch with state root'
                           ' {} but no uncommitted found'
                           .format(THREE_PC_PREFIX, self, stateRoot))
        assert self.unCommitted[0][0] == stateRoot, \
            'The first created batch has ' \
            'not been committed or ' \
            'reverted and yet another ' \
            'batch is trying to be ' \
            'committed, {} {}'\
            .format(self.unCommitted[0][0], stateRoot)
        self._keyValueStorage.setBatch([(idr, val) for idr, val in
                                        self.unCommitted[0][1].items()])
        self.unCommitted = self.unCommitted[1:]

    def getVerkey(self, idr, isCommitted=True):
        seqNo, txnTime, ta, role, verkey = self.get(idr, isCommitted=isCommitted)
        return verkey

    def getRole(self, idr, isCommitted=True):
        seqNo, txnTime, ta, role, verkey = self.get(idr, isCommitted=isCommitted)
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
            seqNo, txnTime, ta, actual_role, verkey = self.get(nym, isCommitted)
        except KeyError:
            return None
        if role and role != actual_role:
            return None
        return {
            ROLE: actual_role or None,
            VERKEY: verkey or None,
            f.IDENTIFIER.nm: ta or None,
            f.SEQ_NO.nm: seqNo or None,
            TXN_TIME: txnTime or None,
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
            return nym
        logger.error('Nym {} not found'.format(nym))
