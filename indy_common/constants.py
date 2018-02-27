from typing import NamedTuple

from plenum.common.constants import TXN_TYPE, TARGET_NYM, ORIGIN, DATA, RAW, \
    ENC, HASH, NAME, VERSION, TYPE, POOL_TXN_TYPES, ALIAS, VERKEY, FORCE
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions

Environment = NamedTuple("Environment", [
    ("poolLedger", str),
    ("domainLedger", str)
])

ROLE = 'role'
NONCE = 'nonce'
ATTRIBUTES = "attributes"
ATTR_NAMES = "attr_names"
ACTION = 'action'
SCHEDULE = 'schedule'
TIMEOUT = 'timeout'
SHA256 = 'sha256'
START = 'start'
CANCEL = 'cancel'
COMPLETE = 'complete'
IN_PROGRESS = 'in_progress'
FAIL = 'fail'
JUSTIFICATION = 'justification'
REINSTALL = 'reinstall'
SIGNATURE_TYPE = 'signature_type'

ID = "id"
TAG = "tag"
CRED_DEF_ID = "credDefId"
ISSUANCE_TYPE = "issuanceType"
MAX_CRED_NUM = "maxCredNum"
PUBLIC_KEYS = "publicKeys"
TAILS_HASH = "tailsHash"
TAILS_LOCATION = "tailsLocation"
SUBMITTER_DID = "submitterDid"
VALUE = "value"
REQ_METADATA = "reqMetadata"
REVOC_REG_DEF_ID = "revocRegDefId"
PREV_ACCUM = "prevAccum"
ACCUM = "accum"
ISSUED = "issued"
REVOKED = "revoked"
ISSUANCE_BY_DEFAULT = "ISSUANCE_BY_DEFAULT"
ISSUANCE_ON_DEMAND = "ISSUANCE_ON_DEMAND"

NULL = 'null'
OWNER = '<owner>'

LAST_TXN = "lastTxn"
TXNS = "Txns"

ENC_TYPE = "encType"
SKEY = "secretKey"
REF = "ref"
PRIMARY = "primary"
REVOCATION = "revocation"

WRITES = "writes"

allOpKeys = (
    TXN_TYPE,
    TARGET_NYM,
    VERKEY,
    ORIGIN,
    ROLE,
    DATA,
    NONCE,
    REF,
    RAW,
    ENC,
    HASH,
    ALIAS,
    ACTION,
    SCHEDULE,
    TIMEOUT,
    SHA256,
    START,
    CANCEL,
    NAME,
    VERSION,
    JUSTIFICATION,
    SIGNATURE_TYPE,
    FORCE,
    WRITES,
    REINSTALL)

reqOpKeys = (TXN_TYPE,)

# Attribute Names
ENDPOINT = "endpoint"

# Roles
TRUST_ANCHOR = Roles.TRUST_ANCHOR.value
TGB = Roles.TGB.value

# client transaction types
NODE = IndyTransactions.NODE.value
NYM = IndyTransactions.NYM.value
ATTRIB = IndyTransactions.ATTRIB.value
SCHEMA = IndyTransactions.SCHEMA.value
CLAIM_DEF = IndyTransactions.CLAIM_DEF.value
REVOC_REG_DEF = IndyTransactions.REVOC_REG_DEF.value
REVOC_REG_ENTRY = IndyTransactions.REVOC_REG_ENTRY.value
DISCLO = IndyTransactions.DISCLO.value
GET_ATTR = IndyTransactions.GET_ATTR.value
GET_NYM = IndyTransactions.GET_NYM.value
GET_TXNS = IndyTransactions.GET_TXNS.value
GET_SCHEMA = IndyTransactions.GET_SCHEMA.value
GET_CLAIM_DEF = IndyTransactions.GET_CLAIM_DEF.value

POOL_UPGRADE = IndyTransactions.POOL_UPGRADE.value
NODE_UPGRADE = IndyTransactions.NODE_UPGRADE.value

POOL_CONFIG = IndyTransactions.POOL_CONFIG.value

# TXN_TYPE -> (requireds, optionals)
fields = {NYM: ([TARGET_NYM], [ROLE]),
          ATTRIB: ([], [RAW, ENC, HASH]),
          SCHEMA: ([NAME, VERSION, ATTR_NAMES]),
          GET_SCHEMA: ([], []),
          CLAIM_DEF: ([REF, DATA, SIGNATURE_TYPE]),
          GET_CLAIM_DEF: ([REF, ORIGIN, SIGNATURE_TYPE]),
          REVOC_REG_DEF: ([ID, TYPE, TAG, CRED_DEF_ID, VALUE]),
          REVOC_REG_ENTRY: ([REVOC_REG_DEF_ID, TYPE, VALUE]),
          }

CONFIG_TXN_TYPES = {POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG}
IDENTITY_TXN_TYPES = {NYM,
                      ATTRIB,
                      DISCLO,
                      GET_ATTR,
                      GET_NYM,
                      GET_TXNS,
                      SCHEMA,
                      GET_SCHEMA,
                      CLAIM_DEF,
                      GET_CLAIM_DEF}

validTxnTypes = set()
validTxnTypes.update(POOL_TXN_TYPES)
validTxnTypes.update(IDENTITY_TXN_TYPES)
validTxnTypes.update(CONFIG_TXN_TYPES)

CONFIG_LEDGER_ID = 2
JUSTIFICATION_MAX_SIZE = 1000
