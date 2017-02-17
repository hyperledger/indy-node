import os

import leveldb

from plenum.common.log import getlogger

logger = getlogger()


class IdrCache:
    """
    A cache to store a role and verkey of an identifier, this is only used to
    store committed data, if a lookup results in a miss,
    state trie must be checked.
    """
    roleSep = b'\0'
    ownerPrefix = b'\1'
    guardianPrefix = b'\2'

    def __init__(self, basedir: str, name='identity_cache'):
        logger.debug('Initializing identity cache {} at {}'
                     .format(name, basedir))
        self._basedir = basedir
        self._name = name
        self._db = None
        self.open()

    @staticmethod
    def packIdrValue(verkey=None, role=None):
        if verkey is None:
            verkey = b''
        if role is None:
            role = b''
        return b'{}{}{}'.__format__(verkey, IdrCache.roleSep, role)

    @staticmethod
    def unpackIdrValue(value):
        hasGuardian = None
        part, role = value.rsplit(IdrCache.roleSep, 1)
        if part:
            if part[0] == IdrCache.ownerPrefix:
                hasGuardian = False
                verkey = part[1:]
            elif part[0] == IdrCache.guardianPrefix:
                hasGuardian = True
                guardian = part[1:]
            else:
                assert 'No acceptable prefix found while parsing {}'.format(part)
        return hasGuardian, (guardian if hasGuardian else verkey), role

    def get(self, idr):
        idr = str.encode(idr)
        value = self._db.Get(idr)
        hasGuardian, iv, r = self.unpackIdrValue(value)
        return hasGuardian, iv.decode(), r.decode()

    def set(self, idr, guardian=None, verkey=None, role=None):
        idr = idr.encode()
        if isinstance(verkey, str):
            verkey = verkey.encode()
        if isinstance(role, str):
            role = role.encode()
        self._db.Put(idr, self.packIdrValue(verkey, role))

    def close(self):
        self._db = None

    def open(self):
        self._db = leveldb.LevelDB(self.dbName)

    @property
    def dbName(self):
        return os.path.join(self._basedir, self._name)

    def getVerkey(self, idr):
        verkey, _ = self.get(idr)
        return verkey

    def getRole(self, idr):
        _, role = self.get(idr)
        return role
