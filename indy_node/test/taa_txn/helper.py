from random import randint

from indy_common.constants import TXN_ATHR_AGRMT
from plenum.common.constants import TXN_TYPE, CURRENT_PROTOCOL_VERSION
from plenum.common.types import OPERATION, f
from plenum.common.util import randomString


def gen_txn_athr_agrmt(did: str, version: str, text: str):
    return {
        OPERATION: {
            TXN_TYPE: TXN_ATHR_AGRMT,
            'text': text,
            'version': version
        },
        f.IDENTIFIER.nm: did,
        f.REQ_ID.nm: randint(1, 2147483647),
        f.PROTOCOL_VERSION.nm: CURRENT_PROTOCOL_VERSION
    }


def gen_random_txn_athr_agrmt(did: str):
    text = randomString(1024)
    version = randomString(16)
    return gen_txn_athr_agrmt(did, version, text)
