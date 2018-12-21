import random

from plenum.common.util import randomString


def add_to_idr(idr, identifier, role):
    random_s = randomString()
    idr.set(identifier,
            seqNo=5,
            txnTime=random.randint(10, 100000),
            ta=random_s,
            role=role,
            verkey=random_s,
            isCommitted=True)
