from typing import Any, Optional, Tuple, Union

from indy_node.server.request_handlers.domain_req_handlers.attribute_handler import AttributeHandler
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from indy_common.constants import ATTRIB, GET_ATTR, TIMESTAMP
from indy_node.server.request_handlers.utils import validate_attrib_keys
from plenum.common.constants import RAW, ENC, HASH, TARGET_NYM, DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_txn_time
from plenum.server.database_manager import DatabaseManager
from stp_core.common.log import getlogger
from plenum.server.request_handlers.utils import decode_state_value

logger = getlogger()


class GetAttributeHandler(ReadRequestHandler):

    def __init__(self, node, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_ATTR, DOMAIN_LEDGER_ID)
        self.node = node

    def get_result(self, request: Request):
        self._validate_request_type(request)
        timestamp = request.operation.get(TIMESTAMP)
        seq_no = request.operation.get("seqNo")
        if timestamp and seq_no:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                "Cannot resolve nym with both seqNo and timestamp present",
            )
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
            self.get_attr(
                did=nym,
                key=attr_key,
                attr_type=attr_type,
                timestamp=timestamp,
                seq_no=seq_no,
            )
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

    def get_attr(
        self,
        did: str,
        key: str,
        attr_type,
        timestamp,
        seq_no,
        is_committed=True
    ) -> (str, int, int, list):
        assert did is not None
        assert key is not None
        path = AttributeHandler.make_state_path_for_attr(did, key, attr_type == HASH)
        try:
            hashed_val, last_seq_no, last_update_time, proof = \
                self.lookup_optionally_by_timestamp_seqNo(path, timestamp, seq_no, is_committed, with_proof=True)
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

    def lookup_optionally_by_timestamp_seqNo(self, path, timestamp, seq_no, is_committed=True, with_proof=False) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :param is_committed: queries the committed state root if True else the uncommitted root
        :param with_proof: creates proof if True
        :return: data
        """
        assert path is not None
        if timestamp:
            encoded, proof = self._get_value_by_timestamp_from_state(
                path, timestamp, with_proof=True
            )
        elif seq_no:
            encoded, proof = self._get_value_by_seq_no_from_state(
                path, seq_no, with_proof=True
            )
        head_hash = self.state.committedHeadHash if is_committed else self.state.headHash
        encoded, proof = self._get_value_from_state(path, head_hash, with_proof=with_proof)
        if encoded:
            value, last_seq_no, last_update_time = decode_state_value(encoded)
            return value, last_seq_no, last_update_time, proof
        return None, None, None, proof

    # TODO: remove this methods when it is available in plenum
    def _get_value_by_timestamp_from_state(
        self, path: bytes, timestamp: Optional[str], with_proof=False
    ) -> Tuple[Optional[Union[bytes, str]], Any]:
        """Return the value and proof at a time in the past or None if it didn't exist.

        If no value is found at timestamp, return (None, None).
        """
        past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            return self._get_value_from_state(
                path, head_hash=past_root, with_proof=with_proof
            )

        return None, None

    # TODO: remove this methods when it is available in plenum
    def _get_value_by_seq_no_from_state(
        self, path: bytes, seq_no: str, with_proof=False,
    ) -> Tuple[Optional[Union[bytes, str]], Any]:
        """Return the value and proof when txn identified by seqNo was committed to the ledger.

        If not found, return (None, None).
        """
        db = self.database_manager.get_database(DOMAIN_LEDGER_ID)
        txn = self.node.getReplyFromLedger(db.ledger, seq_no, write=False)

        if txn and "result" in txn:
            timestamp = get_txn_time(txn.result)
            return self._get_value_by_timestamp_from_state(
                path, timestamp=timestamp, with_proof=with_proof
            )
        else:
            return None, None
