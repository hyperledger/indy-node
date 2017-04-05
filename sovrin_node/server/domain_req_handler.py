import json

from plenum.common.exceptions import InvalidClientRequest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH
from plenum.server.domain_req_handler import RequestHandler
from sovrin_common.auth import Authoriser
from sovrin_common.constants import NYM, ROLE, ATTRIB


class DomainReqHandler(RequestHandler):
    def __init__(self, ledger, state, requestProcessor):
        super().__init__(ledger, state)

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
