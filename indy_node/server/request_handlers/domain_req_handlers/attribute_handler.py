from indy_common.state import domain

from indy_common.constants import ATTRIB
from indy_node.server.request_handlers.utils import validate_attrib_keys
from plenum.common.constants import DOMAIN_LEDGER_ID, RAW, ENC, HASH, TARGET_NYM
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest

from plenum.common.request import Request
from plenum.common.txn_util import get_type, get_request_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class AttributeHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, ATTRIB, DOMAIN_LEDGER_ID)

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        if not validate_attrib_keys(operation):
            raise InvalidClientRequest(identifier, req_id,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        if not (not operation.get(TARGET_NYM) or
                self.__has_nym(operation[TARGET_NYM], is_committed=False)):
            raise InvalidClientRequest(identifier, req_id,
                                       '{} should be added before adding '
                                       'attribute for it'.
                                       format(TARGET_NYM))

        if operation.get(TARGET_NYM) and operation[TARGET_NYM] != identifier and \
                not self.database_manager.idr_cache.getOwnerFor(operation[TARGET_NYM],
                                                                isCommitted=False) == identifier:
            raise UnauthorizedClientRequest(
                identifier,
                req_id,
                "Only identity owner/guardian can add attribute "
                "for that identity")

    def gen_state_key(self, txn):
        self._validate_txn_type(txn)
        path = domain.prepare_attr_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, is_committed=True) -> None:
        """
        The state trie stores the hash of the whole attribute data at:
            the did+attribute name if the data is plaintext (RAW)
            the did+hash(attribute) if the data is encrypted (ENC)
        If the attribute is HASH, then nothing is stored in attribute store,
        the trie stores a blank value for the key did+hash
        """
        self._validate_txn_type(txn)
        attr_type, path, value, hashed_value, value_bytes = domain.prepare_attr_for_state(txn)
        self.state.set(path, value_bytes)
        if attr_type != HASH:
            self.database_manager.attribute_store.set(hashed_value, value)

    def __has_nym(self, nym, is_committed: bool = True):
        return self.database_manager.idr_cache.hasNym(nym, isCommitted=is_committed)
