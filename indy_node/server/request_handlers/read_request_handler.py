from indy_common.state import domain
from plenum.common.constants import DATA, TXN_TIME, STATE_PROOF
from plenum.common.plenum_protocol_version import PlenumProtocolVersion
from plenum.common.types import f

from plenum.server.request_handlers.handler_interfaces.read_request_handler import \
    ReadRequestHandler as PReadRequestHandler


class ReadRequestHandler(PReadRequestHandler):

    def lookup(self, path, is_committed=True, with_proof=False) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :param is_committed: queries the committed state root if True else the uncommitted root
        :param with_proof: creates proof if True
        :return: data
        """
        assert path is not None
        head_hash = self.state.committedHeadHash if is_committed else self.state.headHash
        encoded, proof = self._get_value_from_state(path, head_hash, with_proof=with_proof)
        if encoded:
            value, last_seq_no, last_update_time = domain.decode_state_value(encoded)
            return value, last_seq_no, last_update_time, proof
        return None, None, None, proof

    @staticmethod
    def make_result(request, data, last_seq_no, update_time, proof):
        result = {**request.operation, **{
            DATA: data,
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
            f.SEQ_NO.nm: last_seq_no,
            TXN_TIME: update_time
        }}
        if proof and request.protocolVersion and \
                request.protocolVersion >= PlenumProtocolVersion.STATE_PROOF_SUPPORT.value:
            result[STATE_PROOF] = proof

        # Do not inline please, it makes debugging easier
        return result
