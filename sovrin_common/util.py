import datetime
import random
from typing import Tuple, Union, TypeVar, List, Callable

import libnacl.secret
from base58 import b58decode
from plenum.common.signing import serializeMsg
from plenum.common.types import f
from plenum.common.util import isHex, error, cryptonymToHex
from stp_core.crypto.nacl_wrappers import Verifier


def getMsgWithoutSig(msg, sigFieldName=f.SIG.nm):
    msgWithoutSig = {}
    for k, v in msg.items():
        if k != sigFieldName:
            msgWithoutSig[k] = v
    return msgWithoutSig


def verifySig(identifier, signature, msg) -> bool:
    key = cryptonymToHex(identifier) if not isHex(
        identifier) else identifier
    ser = serializeMsg(msg)
    b64sig = signature.encode('utf-8')
    sig = b58decode(b64sig)
    vr = Verifier(key)
    return vr.verify(sig, ser)


def getSymmetricallyEncryptedVal(val, secretKey: Union[str, bytes] = None) -> \
        Tuple[str, str]:
    """
    Encrypt the provided value with symmetric encryption

    :param val: the value to encrypt
    :param secretKey: Optional key, if provided should be either in hex or bytes
    :return: Tuple of the encrypted value and secret key encoded in hex
    """

    if isinstance(val, str):
        val = val.encode("utf-8")
    if secretKey:
        if isHex(secretKey):
            secretKey = bytes(bytearray.fromhex(secretKey))
        elif not isinstance(secretKey, bytes):
            error("Secret key must be either in hex or bytes")
        box = libnacl.secret.SecretBox(secretKey)
    else:
        box = libnacl.secret.SecretBox()

    return box.encrypt(val).hex(), box.sk.hex()


def getSymmetricallyDecryptedVal(val, secretKey: Union[str, bytes]) -> str:
    if isHex(val):
        val = bytes(bytearray.fromhex(val))
    elif isinstance(val, str):
        val = val.encode("utf-8")
    if isHex(secretKey):
        secretKey = bytes(bytearray.fromhex(secretKey))
    elif isinstance(secretKey, str):
        secretKey = secretKey.encode()
    box = libnacl.secret.SecretBox(secretKey)
    return box.decrypt(val).decode()


def dateTimeEncoding(obj):
    if isinstance(obj, datetime.datetime):
        return int(obj.strftime('%s'))
    raise TypeError('Not sure how to serialize %s' % (obj,))


def getNonce(length=32):
    hexChars = [hex(i)[2:] for i in range(0, 16)]
    return "".join([random.choice(hexChars) for i in range(length)])


# TODO: Should have a timeout, should not have kwargs
def ensureReqCompleted(loop, reqKey, client, clbk=None, pargs=None, kwargs=None,
                       cond=None):
    reply, err = client.replyIfConsensus(*reqKey)
    if err is None and reply is None and (cond is None or not cond()):
        loop.call_later(.2, ensureReqCompleted, loop,
                        reqKey, client, clbk, pargs, kwargs, cond)
    elif clbk:
        # TODO: Do something which makes reply and error optional in the
        # callback.
        # TODO: This is kludgy, but will be resolved once we move away from
        # this callback pattern
        if pargs is not None and kwargs is not None:
            clbk(reply, err, *pargs, **kwargs)
        elif pargs is not None and kwargs is None:
            clbk(reply, err, *pargs)
        elif pargs is None and kwargs is not None:
            clbk(reply, err, **kwargs)
        else:
            clbk(reply, err)


def getNonceForProof(nonce):
    return int(nonce, 16)


T = TypeVar('T')


def getIndex(predicateFn: Callable[[T], bool], items: List[T]) -> int:
    """
    Finds the index of an item in list, which satisfies predicate
    :param predicateFn: predicate function to run on items of list
    :param items: list of tuples
    :return: first index for which predicate function returns True
    """
    try:
        return next(i for i, v in enumerate(items) if predicateFn(v))
    except StopIteration:
        return -1
