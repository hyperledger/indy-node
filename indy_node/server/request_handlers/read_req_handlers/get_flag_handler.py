from typing import Any, Dict, Optional, Tuple, cast, Union
from common.serializers.serialization import config_state_serializer
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.node import Node
from indy_common.constants import CONFIG_LEDGER_ID, GET_FLAG, FLAG_NAME, VERSION_ID, VERSION_TIME
from indy_common.state.state_constants import LAST_SEQ_NO, LAST_UPDATE_TIME
from indy_node.server.request_handlers.config_req_handlers.flag_handler import FlagRequestHandler
from indy_node.server.request_handlers.read_req_handlers.version_read_request_handler import VersionReadRequestHandler
from storage.state_ts_store import StateTsDbStorage


class GetFlagRequestHandler(VersionReadRequestHandler):
    """Flag Read Request handler with historic lookup."""

    def __init__(self, node: Node, database_manager: DatabaseManager):
        super().__init__(node, database_manager, GET_FLAG, CONFIG_LEDGER_ID)
        self.timestamp_store: StateTsDbStorage = cast(
            StateTsDbStorage, self.database_manager.ts_store
        )
        self.state_serializer = config_state_serializer

    def get_result(self, request: Request) -> Dict[str, Any]:
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

        flag_data, proof = self.deserialize(self.lookup_version(
            path, seq_no=seq_no, timestamp=timestamp, with_proof=True
        ))

        last_seq_no = None
        update_time = None
        if flag_data:
            last_seq_no = flag_data[LAST_SEQ_NO]
            update_time = flag_data[LAST_UPDATE_TIME]

        result = self.make_result(
            request=request,
            data=flag_data,
            proof=proof,
            last_seq_no=last_seq_no,
            update_time=update_time
        )
        return result

    def lookup_key(self, flag: str, seq_no=None, timestamp=None) -> Tuple[Optional[Union[bytes, str]], Any]:
        """Lookup a flag from the ledger state and return only the value"""
        path = FlagRequestHandler.make_state_path_for_flag(flag)
        value, _ = self.deserialize(self.lookup_version(path, seq_no, timestamp, with_proof=False))
        return value

    def deserialize(self, input: Tuple[Optional[Union[bytes, str]], Any]) -> Tuple[Optional[Union[bytes, str]], Any]:
        (value, proof) = input
        if value:
            value = self.state_serializer.deserialize(value)
        return (value, proof)
