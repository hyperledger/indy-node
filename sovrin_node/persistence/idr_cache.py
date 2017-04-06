import os

import leveldb
from collections import OrderedDict
import rlp

from plenum.common.constants import VERKEY, TRUSTEE, STEWARD, GUARDIAN
from sovrin_common.constants import ROLE, TGB, TRUST_ANCHOR
from stp_core.common.log import getlogger

logger = getlogger()


class IdrCache:
    """
    A cache to store a role and verkey of an identifier, this is only used to
    store committed data, if a lookup results in a miss,
    state trie must be checked.
    The key is the identifier and value is a pack of fields
    The first byte indicates whether the identifier has a guardian or not,
    if it has then the next few bytes will be the guardian's identifier
    otherwise they will be the verkey. Then there is delimiter byte after which
    the value of role starts. eg.
    Value in case of guardian: '\2<guardian's DID>\0<role of the DID>'
    Value in case of no guardian: '\1<verkey of the DID>\0<role of the DID>'
    """

    roleSep = b'\0' # This byte should not be present in any of the role values
    ownerPrefix = b'\1'
    guardianPrefix = b'\2'

    def __init__(self, basedir: str, name):
        logger.debug('Initializing identity cache {} at {}'
                     .format(name, basedir))
        self._basedir = basedir
        self._name = name
        self._db = None
        self.open()
        # OrderedDict where key is the batch seqNo and value is a
        # dictionary similar to cache which can be queried like the
        # database, i.e `self._db`. Keys (state roots are purged) when they
        # get committed or reverted.
        self.unCommitted = OrderedDict() # type: Dict[int, OrderedDict]

        # Relevant NYMs operation done in current batch, in order
        self.currentBatchOps = []   # type: List[Tuple]

    @staticmethod
    def getPrefixAndIv(guardian=None, verkey=None):
        # prefix = IdrCache.guardianPrefix if guardian else IdrCache.ownerPrefix
        iv = guardian if guardian else verkey
        prefix = b'1' if guardian else b'0'
        return prefix, iv

    @staticmethod
    def packIdrValue(role=None, verkey=None, guardian=None):
        prefix, iv = IdrCache.getPrefixAndIv(guardian, verkey)
        if role is None:
            role = b''
        if iv is None:
            iv = b''
        # return '{}{}{}{}'.format(prefix, iv, IdrCache.roleSep, role).encode()
        return rlp.encode([prefix, iv, role])

    @staticmethod
    def unpackIdrValue(value):
        hasGuardian = None
        # part, role = value.rsplit(IdrCache.roleSep, 1)
        # if part:
        #     if part[0] == IdrCache.ownerPrefix:
        #         hasGuardian = False
        #         verkey = part[1:]
        #     elif part[0] == IdrCache.guardianPrefix:
        #         hasGuardian = True
        #         guardian = part[1:]
        #     else:
        #         assert 'No acceptable prefix found while parsing {}'.format(part)
        prf, iv, role = rlp.decode(value)
        hasGuardian = True if prf == b'1' else False
        return hasGuardian, iv, role

    def get(self, idr, isCommitted=True):
        idr = idr.encode()
        if isCommitted:
            value = self._db.Get(idr)
        else:
            # Looking for uncommitted values, iterating over `self.unCommitted`
            # in reverse to get the latest value
            for i, cache in reversed(self.unCommitted.items()):
                if idr in cache:
                    value = cache[idr]
                    break
            else:
                value = self._db.Get(idr)
        hasGuardian, iv, r = self.unpackIdrValue(value)
        return hasGuardian, iv.decode(), r.decode()

    def set(self, idr, guardian=None, verkey=None, role=None, isCommitted=True):
        idr = idr.encode()
        if isinstance(guardian, str):
            guardian = guardian.encode()
        if isinstance(verkey, str):
            verkey = verkey.encode()
        if isinstance(role, str):
            role = role.encode()

        val = self.packIdrValue(role, verkey, guardian)
        if isCommitted:
            self._db.Put(idr, val)
        else:
            self.currentBatchOps.append((idr, val))

    def close(self):
        self._db = None

    def open(self):
        self._db = leveldb.LevelDB(self.dbName)

    @property
    def dbName(self):
        return os.path.join(self._basedir, self._name)

    def currentBatchCreated(self, seqNo):
        self.unCommitted[seqNo] = OrderedDict(self.currentBatchOps)
        self.currentBatchOps = []

    def setVerkey(self, idr, verkey):
        # This method acts as if guardianship is being terminated.
        _, _, role = self.get(idr)
        self.set(idr, guardian=None, verkey=verkey, role=role)

    def setRole(self, idr, role):
        hasGuardian, iv, _ = self.get(idr)
        if hasGuardian:
            g = iv
            v = None
        else:
            g = None
            v = iv
        self.set(idr, guardian=g, verkey=v, role=role)

    def getVerkey(self, idr, isCommitted=True):
        hasGuardian, iv, role = self.get(idr, isCommitted=isCommitted)
        return '' if hasGuardian else iv

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
            hasGuardian, iv, r = self.get(nym, isCommitted)
        except KeyError:
            return None
        if role and role != r:
            return None
        rv = {ROLE: r}
        if hasGuardian:
            rv[GUARDIAN] = iv
        else:
            rv[VERKEY] = iv
        return rv

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
        return bool(self.getTGB(nym))

    def hasSteward(self, nym, isCommitted=True):
        return bool(self.getSteward(nym, isCommitted=isCommitted))

    def hasTrustAnchor(self, nym, isCommitted=True):
        return bool(self.getTrustAnchor(nym, isCommitted=isCommitted))

    def hasNym(self, nym, isCommitted=True):
        return bool(self.getNym(nym, isCommitted=isCommitted))

    def getOwnerFor(self, nym, isCommitted=True):
        nymData = self.getNym(nym, isCommitted=isCommitted)
        if nymData:
            if VERKEY not in nymData:
                return nymData[GUARDIAN]
            else:
                return nym
        logger.error('Nym {} not found'.format(nym))
