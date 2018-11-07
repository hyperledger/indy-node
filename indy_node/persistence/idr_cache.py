import rlp

from indy_common.constants import ROLE, TRUST_ANCHOR
from plenum.common.constants import VERKEY, TRUSTEE, STEWARD, THREE_PC_PREFIX, \
    TXN_TIME
from plenum.common.types import f
from storage.kv_store import KeyValueStorage
from storage.optimistic_kv_store import OptimisticKVStore
from stp_core.common.log import getlogger

logger = getlogger()


class IdrCache(OptimisticKVStore):
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
        super().__init__(self._keyValueStorage)
        self._name = name

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
        idr = idr.encode()
        value = super().get(idr, is_committed=isCommitted)
        return self.unpackIdrValue(value)

    def set(self, idr, seqNo, txnTime,
            ta=None, role=None, verkey=None, isCommitted=True):
        idr = idr.encode()
        val = self.packIdrValue(seqNo, txnTime, ta, role, verkey)
        super().set(idr, val, is_committed=isCommitted)

    def close(self):
        self._keyValueStorage.close()

    def currentBatchCreated(self, stateRoot):
        super().create_batch_from_current(stateRoot)

    def batchRejected(self):
        super().reject_batch()

    def onBatchCommitted(self, stateRoot):
        # Commit an already created batch
        batch_idr = super().first_batch_idr
        if batch_idr is None:
            logger.warning('{}{} is trying to commit a batch with state root'
                           ' {} but no uncommitted found'
                           .format(THREE_PC_PREFIX, self, stateRoot))
            return
        if batch_idr != stateRoot:
            logger.warning('{}{}: The first created batch has not been '
                           'committed or reverted and yet another batch is '
                           'trying to be committed, {} {}'.
                           format(THREE_PC_PREFIX, self,
                                  self.un_committed[0][0], stateRoot))
            return

        try:
            return super().commit_batch()
        except ValueError:
            logger.warning('{}{} found no uncommitted batch'.
                           format(THREE_PC_PREFIX, self))

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

    def getSteward(self, nym, isCommitted=True):
        return self.getNym(nym, STEWARD, isCommitted=isCommitted)

    def getTrustAnchor(self, nym, isCommitted=True):
        return self.getNym(nym, TRUST_ANCHOR, isCommitted=isCommitted)

    def hasTrustee(self, nym, isCommitted=True):
        return bool(self.getTrustee(nym, isCommitted=isCommitted))

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
        logger.info('Nym {} not found'.format(nym))
