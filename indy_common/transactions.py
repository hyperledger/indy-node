from enum import Enum

from plenum.common.transactions import PlenumTransactions


class IndyTransactions(Enum):
    #  These numeric constants CANNOT be changed once they have been used,
    #  because that would break backwards compatibility with the ledger
    #  Also the numeric constants CANNOT collide with transactions in plenum
    NODE = PlenumTransactions.NODE.value
    NYM = PlenumTransactions.NYM.value
    ATTRIB = "100"
    SCHEMA = "101"
    CLAIM_DEF = "102"

    DISCLO = "103"
    GET_ATTR = "104"
    GET_NYM = "105"
    GET_TXNS = PlenumTransactions.GET_TXN.value
    GET_SCHEMA = "107"
    GET_CLAIM_DEF = "108"

    POOL_UPGRADE = "109"
    NODE_UPGRADE = "110"

    POOL_CONFIG = "111"

    CHANGE_KEY = "112"

    def __str__(self):
        return self.name
