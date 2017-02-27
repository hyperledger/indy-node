import os

import leveldb

from plenum.common.log import getlogger

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

    def __init__(self, basedir: str, name='identity_cache'):
        logger.debug('Initializing identity cache {} at {}'
                     .format(name, basedir))
        self._basedir = basedir
        self._name = name
        self._db = None
        self.open()

    @staticmethod
    def getPrefixAndIv(guardian=None, verkey=None):
        prefix = IdrCache.guardianPrefix if guardian else IdrCache.ownerPrefix
        iv = guardian if guardian else verkey
        return prefix, iv

    @staticmethod
    def packIdrValue(role=None, verkey=None, guardian=None):
        prefix, iv = IdrCache.getPrefixAndIv(guardian, verkey)
        if role is None:
            role = b''
        if iv is None:
            iv = b''
        return b'{}{}{}{}'.__format__(prefix, iv, IdrCache.roleSep, role)

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
        if not value:
            raise KeyError
        hasGuardian, iv, r = self.unpackIdrValue(value)
        return hasGuardian, iv.decode(), r.decode()

    def set(self, idr, guardian=None, verkey=None, role=None):
        idr = idr.encode()
        if isinstance(guardian, str):
            guardian = guardian.encode()
        if isinstance(verkey, str):
            verkey = verkey.encode()
        if isinstance(role, str):
            role = role.encode()
        self._db.Put(idr, self.packIdrValue(role, verkey, guardian))

    def close(self):
        self._db = None

    def open(self):
        self._db = leveldb.LevelDB(self.dbName)

    @property
    def dbName(self):
        return os.path.join(self._basedir, self._name)

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

    def getVerkey(self, idr):
        hasGuardian, iv, role = self.get(idr)
        return '' if hasGuardian else iv

    def getRole(self, idr):
        _, _, role = self.get(idr)
        return role
