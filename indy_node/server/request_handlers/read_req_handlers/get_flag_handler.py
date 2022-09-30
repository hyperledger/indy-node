from typing import Any, Optional, Tuple, cast, Union

from common.serializers.serialization import config_state_serializer
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.node import Node
from indy_common.constants import CONFIG_LEDGER_ID, GET_FLAG, FLAG_NAME, VERSION_ID, VERSION_TIME
from storage.state_ts_store import StateTsDbStorage

from indy_node.server.request_handlers.config_req_handlers.flag_handler import FlagRequestHandler
from indy_node.server.request_handlers.read_req_handlers.version_read_request_handler import VersionReadRequestHandler


class GetFlagRequestHandler(VersionReadRequestHandler):
    """Flag Read Request handler with historic lookup."""

    def __init__(self, node: Node, database_manager: DatabaseManager):
        super().__init__(node, database_manager, GET_FLAG, CONFIG_LEDGER_ID)
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

        timestamp = request.operation.get(VERSION_TIME)
        seq_no = request.operation.get(VERSION_ID)

        if timestamp and seq_no:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                f"{VERSION_ID} and {VERSION_TIME} are mutually exclusive; only one should be "
                "specified",
            )
        return self.deserialize(self.lookup_version(path, seq_no, timestamp, with_proof=True))

    def lookup_key(self, flag: str, seq_no=None, timestamp=None):
        """Lookup a flag from the ledger state and return only the value"""
        path = FlagRequestHandler.make_state_path_for_flag(flag)
        return self.deserialize(self.lookup_version(path, seq_no, timestamp, with_proof=False))[0]

    def deserialize(self, input: Tuple[Optional[Union[bytes, str]], Any]):
        (value, proof) = input
        if value:
            value = self.state_serializer.deserialize(value)
        return (value, proof)
