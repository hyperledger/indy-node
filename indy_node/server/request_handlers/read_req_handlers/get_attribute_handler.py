from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler

from indy_common.state import domain

from indy_common.constants import ATTRIB, GET_ATTR

from indy_node.server.request_handlers.utils import validate_attrib_keys
from plenum.common.constants import RAW, ENC, HASH, TARGET_NYM, DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data
from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger

logger = getlogger()


class GetAttributeHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_ATTR, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        if not validate_attrib_keys(operation):
            raise InvalidClientRequest(identifier, req_id,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))
        nym = operation[TARGET_NYM]
        if RAW in operation:
            attr_type = RAW
        elif ENC in operation:
            # If attribute is encrypted, it will be queried by its hash
            attr_type = ENC
        else:
            attr_type = HASH
        attr_key = operation[attr_type]
        value, last_seq_no, last_update_time, proof = \
            self.get_attr(did=nym, key=attr_key, attr_type=attr_type)
        attr = None
        if value is not None:
            if HASH in operation:
                attr = attr_key
            else:
                attr = value
        return self.make_result(request=request,
                                data=attr,
                                last_seq_no=last_seq_no,
                                update_time=last_update_time,
                                proof=proof)

    def get_attr(self,
                 did: str,
                 key: str,
                 attr_type,
                 is_committed=True) -> (str, int, int, list):
        assert did is not None
        assert key is not None
        path = domain.make_state_path_for_attr(did, key, attr_type == HASH)
        try:
            hashed_val, last_seq_no, last_update_time, proof = \
                self.lookup(path, is_committed, with_proof=True)
        except KeyError:
            return None, None, None, None
        if not hashed_val or hashed_val == '':
            # Its a HASH attribute
            return hashed_val, last_seq_no, last_update_time, proof
        else:
            try:
                value = self.database_manager.attribute_store.get(hashed_val)
            except KeyError:
                logger.error('Could not get value from attribute store for {}'
                             .format(hashed_val))
                return None, None, None, None
        return value, last_seq_no, last_update_time, proof
