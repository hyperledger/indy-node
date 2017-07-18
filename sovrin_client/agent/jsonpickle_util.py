import jsonpickle

from anoncreds.protocol.types import PublicKey, RevocationPublicKey, \
    SecretKey, RevocationSecretKey, AccumulatorSecretKey
from anoncreds.protocol.utils import toDictWithStrValues, fromDictWithStrValues

DATA_KEY = 'py/integer-element'


class CommonIntegerElementHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data[DATA_KEY] = obj.toStrDict()
        return data

    def restore(self, obj):
        cls = self._getClass()
        return cls.fromStrDict(obj[DATA_KEY])

    def _getClass(self):
        raise NotImplemented


class PublicKeyHandler(CommonIntegerElementHandler):
    def _getClass(self):
        return PublicKey


class RevocationPublicKeyHandler(CommonIntegerElementHandler):
    def _getClass(self):
        return RevocationPublicKey


class SecretKeyHandler(CommonIntegerElementHandler):
    def _getClass(self):
        return SecretKey


class RevocationSecretKeyHandler(CommonIntegerElementHandler):
    def _getClass(self):
        return RevocationSecretKey


class AccumulatorSecretKeyHandler(CommonIntegerElementHandler):
    def _getClass(self):
        return AccumulatorSecretKey


def setUpJsonpickle():
    customHandlers = [
        (PublicKey, PublicKeyHandler),
        (RevocationPublicKey, RevocationPublicKeyHandler),
        (SecretKey, SecretKeyHandler),
        (RevocationSecretKey, RevocationSecretKeyHandler),
        (AccumulatorSecretKey, AccumulatorSecretKeyHandler)
    ]
    for cls, handler in customHandlers:
        jsonpickle.handlers.register(cls, handler, base=True)
