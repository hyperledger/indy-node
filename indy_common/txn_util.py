import json
from collections import OrderedDict

from plenum.common.constants import TXN_TYPE, TARGET_NYM, \
    DATA, ENC, RAW, HASH, ALIAS, TXN_ID, TRUSTEE, STEWARD, \
    TXN_TIME, VERKEY
from plenum.common.types import f
from indy_common.constants import NYM, ATTRIB, GET_ATTR, \
    ROLE, REF, TRUST_ANCHOR, SIGNATURE_TYPE


def AddNym(target, role=None):
    return newTxn(txnType=NYM, target=target, role=role)


def AddAttr(target, attrData, role=None):
    return newTxn(txnType=ATTRIB, target=target, role=role,
                  enc=attrData)


def GetAttr(target, attrName, role=None):
    queryData = json.dumps({"name": attrName})
    return newTxn(txnType=GET_ATTR, target=target, role=role,
                  data=queryData)


# TODO: Change name to txn or some thing else after discussion
def newTxn(txnType, target=None, data=None, enc=None, raw=None,
           hash=None, role=None):
    txn = {
        TXN_TYPE: txnType
    }
    if target:
        txn[TARGET_NYM] = target
    if data:
        txn[DATA] = data
    if enc:
        txn[ENC] = enc
    if raw:
        txn[RAW] = raw
    if hash:
        txn[HASH] = hash
    if role:
        txn[ROLE] = role
    return txn


def getGenesisTxns():
    return [{ALIAS: "Trustee1",
             TARGET_NYM: "9XNVHKtucEZWh7GrS9S8nRWtVuFQwYLfzGD7pQ7Scjtc",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4a",
             TXN_TYPE: NYM,
             ROLE: TRUSTEE},
            {ALIAS: "Steward1",
             TARGET_NYM: "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward2",
             TARGET_NYM: "2btLJAAb1S3x6hZYdVyAePjqtQYi2ZBSRGy4569RZu8h",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4c",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward3",
             TARGET_NYM: "CECeGXDi6EHuhpwz19uyjjEnsRGNXodFYqCRgdLmLRkt",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4d",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward4",
             TARGET_NYM: "3znAGhp6Tk4kmebhXnk9K3jaTMffu82PJfEG91AeRkq2",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4e",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward5",
             TARGET_NYM: "4AdS22kC7xzb4bcqg9JATuCfAMNcQYcZa1u5eWzs6cSJ",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4f",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward6",
             TARGET_NYM: "4Yk9HoDSfJv9QcmJbLcXdWVgS7nfvdUqiVcvbSu8VBru",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b50",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward7",
             TARGET_NYM: "FR5pWwinRBn35GNhg7bsvw8Q13kRept2pm561DwZCQzT",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b51",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {TXN_TYPE: NYM,
             TARGET_NYM: 'EGRf6ho37aqg5ZZpAyD2mesS6XrNUeSkoVUAbpL6bmJ9',
             ROLE: STEWARD,
             TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b'},
            {TXN_TYPE: NYM,
             f.IDENTIFIER.nm: 'EGRf6ho37aqg5ZZpAyD2mesS6XrNUeSkoVUAbpL6bmJ9',
             TARGET_NYM: 'C2AafyXuDBbcdiHJ8pdJ14PJ17X5KEBjbyfPPJWZFA4b',
             ROLE: TRUST_ANCHOR,
             TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4c'},
            {TXN_TYPE: NYM,
             TARGET_NYM: '4qU9QRZ79CbWuDKUtTvpDUnUiDnkLkwd1i8p2B3gJNU3',
             TXN_ID: '50c2f66f7fda2ece684d1befc667e894b4460cb782f5387d864fa7d5f14c4066',
             ROLE: TRUST_ANCHOR,
             f.IDENTIFIER.nm: 'EGRf6ho37aqg5ZZpAyD2mesS6XrNUeSkoVUAbpL6bmJ9'},
            {TXN_TYPE: NYM,
             TARGET_NYM: 'adityastaging',
             TXN_ID: '77c2f66f7fda2ece684d1befc667e894b4460cb782f5387d864fa7d5f14c4066',
             f.IDENTIFIER.nm: '4qU9QRZ79CbWuDKUtTvpDUnUiDnkLkwd1i8p2B3gJNU3'},
            {TXN_TYPE: NYM,
             TARGET_NYM: 'iosstaging',
             TXN_ID: '91c2f66f7fda2ece684d1befc667e894b4460cb782f5387d864fa7d5f14c4066',
             f.IDENTIFIER.nm: '4qU9QRZ79CbWuDKUtTvpDUnUiDnkLkwd1i8p2B3gJNU3'},
            {ALIAS: "Steward8",
             TARGET_NYM: "6vAQkuCgTm7Jeki3vVhZm1FTAQYCeLE5mSvVRQdiwt1w",
             TXN_ID: "4770beb7e45bf623bd9987af4bd6d6d8eb8b68a4d00fa2a4c6b6f3f0c1c036f8",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward9",
             TARGET_NYM: "6hbecbh36EMK6yAi5NZ9bLZEuRsWFt6qLa2SyMQGXs7H",
             TXN_ID: "4770beb7e45bf623bd9987af4bd6d6d8eb8b68a4d00fa2a4c6b6f3f0c1c036f9",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            ]


def getGenesisTxnsForLocal():
    return [{ALIAS: "Steward1",
             TARGET_NYM: "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward2",
             TARGET_NYM: "3NhxuJKShrpnhxG8VYGkum6mv3HeXWUDfj7ktn5NbeymHoDX",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4c",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward3",
             TARGET_NYM: "CECeGXDi6EHuhpwz19uyjjEnsRGNXodFYqCRgdLmLRkt",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4d",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Steward4",
             TARGET_NYM: "3znAGhp6Tk4kmebhXnk9K3jaTMffu82PJfEG91AeRkq2",
             TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4e",
             TXN_TYPE: NYM,
             ROLE: STEWARD},
            {ALIAS: "Alice",
             TARGET_NYM: "4AdS22kC7xzb4bcqg9JATuCfAMNcQYcZa1u5eWzs6cSJ",
             "identifier": "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683",
             TXN_TYPE: NYM},
            {ALIAS: "Jason",
             TARGET_NYM: "46Kq4hASUdvUbwR7s7Pie3x8f4HRB3NLay7Z9jh9eZsB",
             "identifier": "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919684",
             TXN_TYPE: NYM},
            {ALIAS: "John",
             TARGET_NYM: "3wpYnGqceZ8DzN3guiTd9rrYkWTwTHCChBSuo6cvkXTG",
             "identifier": "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919685",
             TXN_TYPE: NYM},
            {ALIAS: "Les",
             TARGET_NYM: "4Yk9HoDSfJv9QcmJbLcXdWVgS7nfvdUqiVcvbSu8VBru",
             "identifier": "5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC",
             TXN_ID: "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919686",
             TXN_TYPE: NYM}]


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
        (REF, (str, str)),
        (SIGNATURE_TYPE, (str, str))
    ])
