from plenum.common.constants import STEWARD, TXN_ID
from plenum.common.types import f

from indy_common.constants import TXN_TYPE, TARGET_NYM, ROLE, NYM, TRUST_ANCHOR

STEWARD_SEED = b'steward seed used for signer....'
TRUST_ANCHOR_SEED = b'sponsors are people too.........'

GENESIS_TRANSACTIONS = [
    {
        TXN_TYPE: NYM,
        TARGET_NYM: 'bx3ePPiBdRywm16OOmZdtlzF5FGmX06Fj2sAYbMdF18=',
        TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
        ROLE: STEWARD
    },
    {
        TXN_TYPE: NYM,
        f.IDENTIFIER.nm: 'bx3ePPiBdRywm16OOmZdtlzF5FGmX06Fj2sAYbMdF18=',
        TARGET_NYM: 'MnT3cFlVvVu7QO+QzPp5seU14pkOT7go1PsqDWZSrbo=',
        ROLE: TRUST_ANCHOR,
        TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4c'
    },
    # {
    #     TXN_TYPE: NYM,
    #     f.IDENTIFIER.nm: 'OP2h59vBVQerRi6FjoOoMhSTv4CAemeEg4LPtDHaEWw=',
    #     TARGET_NYM: 'ARyM91PzDKveCuqkV9B6TJ5f9YxI8Aw/cz5eDAduNUs=',
    #     ROLE: TRUST_ANCHOR,
    #     TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4d'
    # }
]
