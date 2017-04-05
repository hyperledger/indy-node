from plenum.common.constants import RAW, ENC, HASH, TYPE, VERSION, NAME, DATA, ORIGIN, \
    POOL_TXN_TYPES
from sovrin_common.constants import GET_NYM, GET_ATTR, GET_SCHEMA, GET_ISSUER_KEY, \
    ROLE, NYM, TARGET_NYM, ATTRIB, ATTR_NAMES, SCHEMA, ISSUER_KEY, REF, \
    NODE_UPGRADE, POOL_UPGRADE, DISCLO, GET_TXNS


openTxns = (GET_NYM, GET_ATTR, GET_SCHEMA, GET_ISSUER_KEY)


# TXN_TYPE -> (requireds, optionals)
fields = {NYM: ([TARGET_NYM], [ROLE]),
          ATTRIB: ([], [RAW, ENC, HASH]),
          SCHEMA: ([NAME, VERSION, ATTR_NAMES], [TYPE, ]),
          GET_SCHEMA: ([], []),
          ISSUER_KEY: ([REF, DATA]),
          GET_ISSUER_KEY: ([REF, ORIGIN])
          }

CONFIG_TXN_TYPES = {POOL_UPGRADE, NODE_UPGRADE}
IDENTITY_TXN_TYPES = {NYM,
                      ATTRIB,
                      DISCLO,
                      GET_ATTR,
                      GET_NYM,
                      GET_TXNS,
                      SCHEMA,
                      GET_SCHEMA,
                      ISSUER_KEY,
                      GET_ISSUER_KEY}

CONFIG_LEDGER_ID = 2

validTxnTypes = set()
validTxnTypes.update(POOL_TXN_TYPES)
validTxnTypes.update(IDENTITY_TXN_TYPES)
validTxnTypes.update(CONFIG_TXN_TYPES)

