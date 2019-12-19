from common.serializers.serialization import config_state_serializer
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_handler import TxnAuthorAgreementHandler
from plenum.common.constants import TXN_AUTHOR_AGREEMENT, CONFIG_LEDGER_ID, TXN_AUTHOR_AGREEMENT_VERSION, \
    TXN_AUTHOR_AGREEMENT_TEXT
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.static_taa_helper import StaticTAAHelper
from plenum.server.request_handlers.utils import encode_state_value, decode_state_value


class TxnAuthorAgreementHandlerV1(TxnAuthorAgreementHandler):

    def _update_txn_author_agreement(self, digest, seq_no, txn_time, text, version, retired=False):
        digest = StaticTAAHelper.taa_digest(text, version)
        data = encode_state_value({
            TXN_AUTHOR_AGREEMENT_TEXT: text,
            TXN_AUTHOR_AGREEMENT_VERSION: version
        }, seq_no, txn_time, serializer=config_state_serializer)

        self.state.set(StaticTAAHelper.state_path_taa_digest(digest), data)
        self.state.set(StaticTAAHelper.state_path_taa_latest(), digest)
        self.state.set(StaticTAAHelper.state_path_taa_version(version), digest)
