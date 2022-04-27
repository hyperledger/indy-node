from typing import Any, Mapping

from plenum.common.constants import DOMAIN_LEDGER_ID, ENC, HASH, RAW, TARGET_NYM
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.utils import decode_state_value
from stp_core.common.log import getlogger

from indy_common.constants import ATTRIB, GET_ATTR, VERSION_ID, VERSION_TIME
from indy_node.server.request_handlers.domain_req_handlers.attribute_handler import (
    AttributeHandler,
)
from indy_node.server.request_handlers.read_req_handlers.version_read_request_handler import (
    VersionReadRequestHandler,
)
from indy_node.server.request_handlers.utils import validate_attrib_keys

logger = getlogger()


class GetAttributeHandler(VersionReadRequestHandler):

    def __init__(self, node, database_manager: DatabaseManager):
        super().__init__(node, database_manager, GET_ATTR, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)

        identifier, req_id, operation = get_request_data(request)

        timestamp = operation.get(VERSION_TIME)
        seq_no = operation.get(VERSION_ID)
        if timestamp and seq_no:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                f"{VERSION_ID} and {VERSION_TIME} are mutually exclusive; only one should be "
                "specified",
            )
        # The above check determines whether the request is valid
        # A similar check in VersionReadRequestHandler determines
        # whether the method is used correctly

        if not validate_attrib_keys(operation):
            raise InvalidClientRequest(
                identifier, req_id,
                '{} should have one and only one of '
                '{}, {}, {}'
                .format(ATTRIB, RAW, ENC, HASH)
            )

        attr_type = self._get_attr_type(operation)
        path = AttributeHandler.make_state_path_for_attr(
            operation[TARGET_NYM],
            operation[attr_type],
            attr_type == HASH,
        )

        encoded, proof = self.lookup_version(
            path, seq_no=seq_no, timestamp=timestamp, with_proof=True
        )

        if not encoded:
            return self.make_result(
                request=request,
                data=None,
                last_seq_no=None,
                update_time=None,
                proof=proof
            )

        store_key, last_seq_no, last_update_time = decode_state_value(encoded)

        if attr_type == HASH:
            return self.make_result(
                request=request,
                data=operation[HASH],
                last_seq_no=last_seq_no,
                update_time=last_update_time,
                proof=proof
            )

        store_value = self._get_value_from_attribute_store(store_key)
        return self.make_result(
            request=request,
            data=store_value,
            last_seq_no=last_seq_no,
            update_time=last_update_time,
            proof=proof
        )

    @staticmethod
    def _get_attr_type(operation: Mapping[str, Any]):
        """Return attribute type based on presence of keys in operation."""
        if RAW in operation:
            return RAW
        if ENC in operation:
            return ENC
        return HASH

    def _get_value_from_attribute_store(self, key: str):
        """Retrieve value from attribute store or return None if it doesn't exist."""
        try:
            value = self.database_manager.attribute_store.get(key)
        except KeyError:
            logger.error(
                'Could not get value from attribute store for %s', key
            )
            return None
        return value
