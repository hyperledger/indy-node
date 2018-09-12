from typing import NamedTuple

from plenum.common.constants import TXN_TYPE, TARGET_NYM, ORIGIN, DATA, RAW, \
    ENC, HASH, NAME, VERSION, TYPE, POOL_TXN_TYPES, ALIAS, VERKEY, FORCE
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions

Environment = NamedTuple("Environment", [
    ("poolLedger", str),
    ("domainLedger", str)
])

# SCHEMA
SCHEMA_NAME = "name"
SCHEMA_VERSION = "version"
SCHEMA_ATTR_NAMES = "attr_names"
SCHEMA_FROM = "dest"

# CLAIM DEF
CLAIM_DEF_SIGNATURE_TYPE = "signature_type"
CLAIM_DEF_SCHEMA_REF = "ref"
CLAIM_DEF_TAG = "tag"
CLAIM_DEF_PUBLIC_KEYS = "data"
CLAIM_DEF_FROM = "origin"
CLAIM_DEF_PRIMARY = "primary"
CLAIM_DEF_REVOCATION = "revocation"
CLAIM_DEF_TAG_DEFAULT = "tag"
CLAIM_DEF_CL = "CL"

ROLE = 'role'
NONCE = 'nonce'
ATTRIBUTES = "attributes"
ACTION = 'action'
SCHEDULE = 'schedule'
DATETIME = 'datetime'
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
TAG = 'tag'
PACKAGE = 'package'

REVOC_TYPE = "revocDefType"
ID = "id"
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
ACCUM_FROM = "accum_from"
ACCUM_TO = "accum_to"
ISSUED = "issued"
REVOKED = "revoked"
ISSUANCE_BY_DEFAULT = "ISSUANCE_BY_DEFAULT"
ISSUANCE_ON_DEMAND = "ISSUANCE_ON_DEMAND"
TIMESTAMP = 'timestamp'
FROM = "from"
TO = "to"
STATE_PROOF_FROM = "stateProofFrom"
REVOC_REG_ID = "revocRegId"

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

RESTART_MESSAGE = "restart"
UPGRADE_MESSAGE = "upgrade"
MESSAGE_TYPE = "message_type"

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
TRUST_ANCHOR_STRING = 'TRUST_ANCHOR'
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
GET_REVOC_REG_DEF = IndyTransactions.GET_REVOC_REG_DEF.value
GET_REVOC_REG = IndyTransactions.GET_REVOC_REG.value
GET_REVOC_REG_DELTA = IndyTransactions.GET_REVOC_REG_DELTA.value

POOL_UPGRADE = IndyTransactions.POOL_UPGRADE.value
NODE_UPGRADE = IndyTransactions.NODE_UPGRADE.value
POOL_RESTART = IndyTransactions.POOL_RESTART.value
VALIDATOR_INFO = IndyTransactions.VALIDATOR_INFO.value

POOL_CONFIG = IndyTransactions.POOL_CONFIG.value

CONFIG_TXN_TYPES = {POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG, POOL_RESTART}
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

APP_NAME = "indy-node"
