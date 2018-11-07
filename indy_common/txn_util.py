from collections import OrderedDict

from indy_common.constants import ROLE, CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_SCHEMA_REF
from plenum.common.constants import TXN_TYPE, TARGET_NYM, \
    DATA, ENC, RAW, HASH, ALIAS, TXN_TIME, VERKEY
from plenum.common.types import f


def getTxnOrderedFields():
    return OrderedDict([
        (f.IDENTIFIER.nm, (str, str)),
        (f.REQ_ID.nm, (str, int)),
        (f.SIG.nm, (str, str)),
        (TXN_TIME, (str, int)),
        (TXN_TYPE, (str, str)),
        (TARGET_NYM, (str, str)),
        (VERKEY, (str, str)),
        (DATA, (str, str)),
        (ALIAS, (str, str)),
        (RAW, (str, str)),
        (ENC, (str, str)),
        (HASH, (str, str)),
        (ROLE, (str, str)),
        (CLAIM_DEF_SCHEMA_REF, (str, str)),
        (CLAIM_DEF_SIGNATURE_TYPE, (str, str))
    ])
