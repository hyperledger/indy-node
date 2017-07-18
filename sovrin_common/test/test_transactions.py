from sovrin_common.constants import NYM, NODE, ATTRIB, SCHEMA, CLAIM_DEF, DISCLO, GET_ATTR, GET_NYM, GET_TXNS, \
    GET_SCHEMA, GET_CLAIM_DEF, POOL_UPGRADE, NODE_UPGRADE
from sovrin_common.transactions import SovrinTransactions


def testTransactionsAreEncoded():
    assert NODE == "0"
    assert NYM == "1"
    assert GET_TXNS == "3"
    assert ATTRIB == "100"
    assert SCHEMA == "101"
    assert CLAIM_DEF == "102"
    assert DISCLO == "103"
    assert GET_ATTR == "104"
    assert GET_NYM == "105"
    assert GET_SCHEMA == "107"
    assert GET_CLAIM_DEF == "108"
    assert POOL_UPGRADE == "109"
    assert NODE_UPGRADE == "110"


def testTransactionEnumDecoded():
    assert SovrinTransactions.NODE.name == "NODE"
    assert SovrinTransactions.NYM.name == "NYM"

    assert SovrinTransactions.ATTRIB.name == "ATTRIB"
    assert SovrinTransactions.SCHEMA.name == "SCHEMA"
    assert SovrinTransactions.CLAIM_DEF.name == "CLAIM_DEF"

    assert SovrinTransactions.DISCLO.name == "DISCLO"
    assert SovrinTransactions.GET_ATTR.name == "GET_ATTR"
    assert SovrinTransactions.GET_NYM.name == "GET_NYM"
    assert SovrinTransactions.GET_TXNS.name == "GET_TXNS"
    assert SovrinTransactions.GET_SCHEMA.name == "GET_SCHEMA"
    assert SovrinTransactions.GET_CLAIM_DEF.name == "GET_CLAIM_DEF"
    assert SovrinTransactions.POOL_UPGRADE.name == "POOL_UPGRADE"
    assert SovrinTransactions.NODE_UPGRADE.name == "NODE_UPGRADE"


def testTransactionEnumEncoded():
    assert SovrinTransactions.NODE.value == "0"
    assert SovrinTransactions.NYM.value == "1"
    assert SovrinTransactions.GET_TXNS.value == "3"

    assert SovrinTransactions.ATTRIB.value == "100"
    assert SovrinTransactions.SCHEMA.value == "101"
    assert SovrinTransactions.CLAIM_DEF.value == "102"

    assert SovrinTransactions.DISCLO.value == "103"
    assert SovrinTransactions.GET_ATTR.value == "104"
    assert SovrinTransactions.GET_NYM.value == "105"
    assert SovrinTransactions.GET_SCHEMA.value == "107"
    assert SovrinTransactions.GET_CLAIM_DEF.value == "108"
    assert SovrinTransactions.POOL_UPGRADE.value == "109"
    assert SovrinTransactions.NODE_UPGRADE.value == "110"
