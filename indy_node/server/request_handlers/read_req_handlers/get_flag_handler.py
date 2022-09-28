from typing import Any, Optional, Tuple, cast, Union

from common.serializers.serialization import config_state_serializer
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from indy_common.state.state_constants import MARKER_FLAG
from indy_common.constants import CONFIG_LEDGER_ID, GET_FLAG, FLAG_NAME, FLAG_VALUE, VERSION_ID, VERSION_TIME
from storage.state_ts_store import StateTsDbStorage

from indy_node.server.request_handlers.config_req_handlers.flag_handler import FlagRequestHandler


class GetFlagRequestHandler(ReadRequestHandler):
    """Flag Read Request handler with historic lookup."""

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_FLAG, CONFIG_LEDGER_ID)
        self.timestamp_store: StateTsDbStorage = cast(
            StateTsDbStorage, self.database_manager.ts_store
        )
        self.state_serializer = config_state_serializer

    def get_result(self, request: Request):
        self._validate_request_type(request)
        key = request.operation.get(FLAG_NAME)
        if key is None:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                "Flag name must be provided in get request for config flags"
            )
        path = FlagRequestHandler.make_state_path_for_flag(key)

        # Optional input
        timestamp = request.operation.get(VERSION_TIME)
        return self.deserialize(self.lookup_version(path, timestamp, with_proof=True))

    def lookup_key(self, flag: str, timestamp=None):
        """Lookup a flag from the ledger state and return only the value"""
        path = FlagRequestHandler.make_state_path_for_flag(flag)
        return self.deserialize(self.lookup_version(path, timestamp, with_proof=False))[0]

    def deserialize(self, input: Tuple[Optional[Union[bytes, str]], Any]):
        (value, proof) = input
        if value:
            value = self.state_serializer.deserialize(value)
        return (value, proof)

    def lookup_version(
        self,
        path: bytes,
        timestamp: Optional[int] = None,
        with_proof=False
    ):
        """Lookup a value from the ledger state, optionally retrieving from the past.

        If timestamp is specified and no value is found, returns (None, None).
        If not specified, value in its current state is retrieved, which will
        also return (None, None) if it is not found on the ledger.
        """

        if timestamp:
            past_root = self.timestamp_store.get_equal_or_prev(timestamp, ledger_id=self.ledger_id)
            if past_root:
                return self._get_value_from_state(
                    path, head_hash=past_root, with_proof=with_proof
                )
            return None, None

        return self._get_value_from_state(
            path, with_proof=with_proof
        )
