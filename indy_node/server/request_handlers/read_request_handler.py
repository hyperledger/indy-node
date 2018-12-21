from indy_common.state import domain

from plenum.server.request_handlers.handler_interfaces.read_request_handler import \
    ReadRequestHandler as PReadRequestHandler


class ReadRequestHandler(PReadRequestHandler):

    def lookup(self, path, isCommitted=True, with_proof=False) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :param isCommitted: queries the committed state root if True else the uncommitted root
        :param with_proof: creates proof if True
        :return: data
        """
        assert path is not None
        head_hash = self.state.committedHeadHash if isCommitted else self.state.headHash
        encoded, proof = self.get_value_from_state(path, head_hash, with_proof=with_proof)
        if encoded:
            value, last_seq_no, last_update_time = domain.decode_state_value(encoded)
            return value, last_seq_no, last_update_time, proof
        return None, None, None, proof
