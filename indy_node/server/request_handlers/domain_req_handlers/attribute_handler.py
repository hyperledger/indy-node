from _sha256 import sha256
from copy import deepcopy
from json import JSONDecodeError
from typing import Optional

from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.serialization import attrib_raw_data_serializer
from indy_common.state import domain

from indy_common.constants import ATTRIB
from indy_common.state.state_constants import MARKER_ATTR
from indy_node.server.request_handlers.utils import validate_attrib_keys
from plenum.common.constants import DOMAIN_LEDGER_ID, RAW, ENC, HASH, TARGET_NYM
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.common.txn_util import get_type, get_request_data, get_payload_data, get_seq_no, get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value
from stp_core.common.log import getlogger

logger = getlogger()

ALL_ATR_KEYS = [RAW, ENC, HASH]


class AttributeHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, ATTRIB, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        if not validate_attrib_keys(operation):
            raise InvalidClientRequest(identifier, req_id,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))

        if RAW in operation:
            try:
                get_key = attrib_raw_data_serializer.deserialize(operation[RAW])
                if len(get_key) == 0:
                    raise InvalidClientRequest(identifier, request.reqId,
                                               '"row" attribute field must contain non-empty dict'.
                                               format(TARGET_NYM))
            except JSONDecodeError:
                raise InvalidClientRequest(identifier, request.reqId,
                                           'Attribute field must be dict while adding it as a row field'.
                                           format(TARGET_NYM))

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)

        identifier, req_id, operation = get_request_data(request)

        if not (not operation.get(TARGET_NYM) or self.__has_nym(operation[TARGET_NYM], is_committed=False)):
            raise InvalidClientRequest(identifier, request.reqId,
                                       '{} should be added before adding '
                                       'attribute for it'.
                                       format(TARGET_NYM))

        is_owner = self.database_manager.idr_cache.getOwnerFor(operation[TARGET_NYM],
                                                               isCommitted=False) == identifier
        field = None
        value = None
        for key in (RAW, ENC, HASH):
            if key in operation:
                field = key
                value = operation[key]
                break

        if field == RAW:
            get_key = attrib_raw_data_serializer.deserialize(value)
            get_key = list(get_key.keys())[0]
        else:
            get_key = value

        old_value, seq_no, _ = self._get_attr(operation[TARGET_NYM], get_key, field)

        if seq_no is not None:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=ATTRIB,
                                                              field=field,
                                                              old_value=old_value,
                                                              new_value=value,
                                                              is_owner=is_owner)])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=ATTRIB,
                                                             field=field,
                                                             value=value,
                                                             is_owner=is_owner)])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = self.prepare_attr_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        """
        The state trie stores the hash of the whole attribute data at:
            the did+attribute name if the data is plaintext (RAW)
            the did+hash(attribute) if the data is encrypted (ENC)
        If the attribute is HASH, then nothing is stored in attribute store,
        the trie stores a blank value for the key did+hash
        """
        self._validate_txn_type(txn)
        attr_type, path, value, hashed_value, value_bytes = self.prepare_attr_for_state(txn)
        self.state.set(path, value_bytes)
        if attr_type != HASH:
            self.database_manager.attribute_store.set(hashed_value, value)
        return txn

    def _get_attr(self,
                  did: str,
                  key: str,
                  attr_type,
                  is_commited=False) -> (str, int, int, list):
        assert did is not None
        assert key is not None
        path = AttributeHandler.make_state_path_for_attr(did, key, attr_type == HASH)
        try:
            hashed_val, lastSeqNo, lastUpdateTime = self.get_from_state(path, is_commited)
        except KeyError:
            return None, None, None, None
        if not hashed_val or hashed_val == '':
            # Its a HASH attribute
            return hashed_val, lastSeqNo, lastUpdateTime
        else:
            value = self.database_manager.attribute_store.get(hashed_val)
        return value, lastSeqNo, lastUpdateTime

    def __has_nym(self, nym, is_committed: bool = True):
        return self.database_manager.idr_cache.hasNym(nym, isCommitted=is_committed)

    @staticmethod
    def prepare_attr_for_state(txn, path_only=False):
        """
        Make key(path)-value pair for state from ATTRIB or GET_ATTR
        :return: state path, state value, value for attribute store
        """
        assert get_type(txn) == ATTRIB
        txn_data = get_payload_data(txn)
        nym = txn_data[TARGET_NYM]
        attr_type, attr_key, value = AttributeHandler.parse_attr_txn(txn_data)
        path = AttributeHandler.make_state_path_for_attr(nym, attr_key, attr_type == HASH)
        if path_only:
            return path
        hashed_value = domain.hash_of(value) if value else ''
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        value_bytes = encode_state_value(hashed_value, seq_no, txn_time)
        return attr_type, path, value, hashed_value, value_bytes

    @staticmethod
    def parse_attr_txn(txn_data):
        attr_type, attr = AttributeHandler._extract_attr_typed_value(txn_data)

        if attr_type == RAW:
            data = attrib_raw_data_serializer.deserialize(attr)
            # To exclude user-side formatting issues
            re_raw = attrib_raw_data_serializer.serialize(data,
                                                          toBytes=False)
            key, _ = data.popitem()
            return attr_type, key, re_raw
        if attr_type == ENC:
            return attr_type, attr, attr
        if attr_type == HASH:
            return attr_type, attr, None

    @staticmethod
    def _extract_attr_typed_value(txn_data):
        """
        ATTR and GET_ATTR can have one of 'raw', 'enc' and 'hash' fields.
        This method checks which of them presents and return it's name
        and value in it.
        """
        existing_keys = [key for key in ALL_ATR_KEYS if key in txn_data]
        if len(existing_keys) == 0:
            raise ValueError("ATTR should have one of the following fields: {}"
                             .format(ALL_ATR_KEYS))
        if len(existing_keys) > 1:
            raise ValueError("ATTR should have only one of the following fields: {}"
                             .format(ALL_ATR_KEYS))
        existing_key = existing_keys[0]
        return existing_key, txn_data[existing_key]

    @staticmethod
    def make_state_path_for_attr(did, attr_name, attr_is_hash=False) -> bytes:
        nameHash = sha256(attr_name.encode()).hexdigest() if not attr_is_hash else attr_name
        return "{DID}:{MARKER}:{ATTR_NAME}" \
            .format(DID=did,
                    MARKER=MARKER_ATTR,
                    ATTR_NAME=nameHash).encode()

    def transform_txn_for_ledger(self, txn):
        """
        Creating copy of result so that `RAW`, `ENC` or `HASH` can be
        replaced by their hashes. We do not insert actual attribute data
        in the ledger but only the hash of it.
        """
        txn = deepcopy(txn)
        txn_data = get_payload_data(txn)
        attr_type, _, value = self.parse_attr_txn(txn_data)
        if attr_type in [RAW, ENC]:
            txn_data[attr_type] = domain.hash_of(value) if value else ''

        return txn
