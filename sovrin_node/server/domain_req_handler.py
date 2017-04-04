import json

from plenum.common.exceptions import InvalidClientRequest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH
from plenum.server.domain_req_handler import DomainReqHandler as PHandler
from sovrin_common.auth import Authoriser
from sovrin_common.txn import NYM, ROLE, ATTRIB


class DomainReqHandler(PHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def doStaticValidation(self, identifier, reqId, operation):
        if operation[TXN_TYPE] == NYM:
            role = operation.get(ROLE)
            nym = operation.get(TARGET_NYM)
            if not nym:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} needs to be present".
                                           format(TARGET_NYM))
            if not Authoriser.isValidRole(role):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid role".
                                           format(role))

        if operation[TXN_TYPE] == ATTRIB:
            dataKeys = {RAW, ENC, HASH}.intersection(set(operation.keys()))
            if len(dataKeys) != 1:
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should have one and only one of '
                                           '{}, {}, {}'
                                           .format(ATTRIB, RAW, ENC, HASH))
            if RAW in dataKeys:
                try:
                    json.loads(operation[RAW])
                except:
                    raise InvalidClientRequest(identifier, reqId,
                                               'raw attribute {} should be '
                                               'JSON'.format(operation[RAW]))
