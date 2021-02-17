from common.serializers.serialization import proof_nodes_serializer, state_roots_serializer, config_state_serializer
from plenum.common.constants import MULTI_SIGNATURE, ROOT_HASH, PROOF_NODES


class BatchFeesTracker:
    def __init__(self):
        self.fees_in_current_batch = 0
        self._deducted_fees = {}

    def add_deducted_fees(self, txn_type, seq_no, fees):
        key = "{}#{}".format(txn_type, seq_no)
        self._deducted_fees[key] = fees

    def has_deducted_fees(self, txn_type, seq_no):
        return "{}#{}".format(txn_type, seq_no) in self._deducted_fees


class FeesStaticHelper:

    @staticmethod
    def get_fee_from_state(state, fees_alias=None, is_committed=False, with_proof=False, bls_store=None):
        fees = None
        proof = None
        try:
            fees_key = FeesStaticHelper.build_path_for_set_fees(alias=fees_alias)
            if with_proof:
                root_hash = state.committedHeadHash if is_committed else state.headHash
                proof, serz = state.generate_state_proof(fees_key,
                                                         root=state.get_head_by_hash(root_hash),
                                                         serialize=True,
                                                         get_value=True)
                if serz:
                    serz = state.get_decoded(serz)
                encoded_root_hash = state_roots_serializer.serialize(bytes(root_hash))
                multi_sig = bls_store.get(encoded_root_hash)
                if multi_sig:
                    encoded_proof = proof_nodes_serializer.serialize(proof)
                    proof = {
                        MULTI_SIGNATURE: multi_sig.as_dict(),
                        ROOT_HASH: encoded_root_hash,
                        PROOF_NODES: encoded_proof
                    }
                else:
                    proof = {}
            else:
                serz = state.get(fees_key,
                                 isCommitted=is_committed)
            if serz:
                fees = config_state_serializer.deserialize(serz)
        except KeyError:
            pass
        if with_proof:
            return fees, proof
        return fees

    FEES_STATE_PREFIX = '200'
    FEES_KEY_DELIMITER = ':'
    FEES_KEY_FOR_ALL = 'fees'

    @staticmethod
    def build_path_for_set_fees(alias=None):
        if alias:
            return FeesStaticHelper.FEES_KEY_DELIMITER.join([FeesStaticHelper.FEES_STATE_PREFIX, alias])
        return FeesStaticHelper.FEES_KEY_DELIMITER.join([FeesStaticHelper.FEES_STATE_PREFIX, FeesStaticHelper.FEES_KEY_FOR_ALL])
