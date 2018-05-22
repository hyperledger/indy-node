from abc import abstractmethod, ABCMeta

from copy import deepcopy

from indy_common.state import domain
from indy_common.types import Request
from indy_common.constants import REVOC_REG_DEF_ID, VALUE, ACCUM, PREV_ACCUM, ISSUED, REVOKED
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.txn_util import get_from, get_req_id, get_payload_data


class RevocationStrategy(metaclass=ABCMeta):

    def __init__(self, state):
        self.state = state
        self.author_did = None
        self.revoc_reg_def_id = None
        self.req_id = None

    def set_parameters_from_txn(self, author_did, revoc_reg_def_id, req_id):
        self.author_did = author_did
        self.revoc_reg_def_id = revoc_reg_def_id
        self.req_id = req_id

    def validate(self, current_entry, req: Request):
        self.set_parameters_from_txn(author_did=req.identifier,
                                     revoc_reg_def_id=req.operation[REVOC_REG_DEF_ID],
                                     req_id=req.reqId)
        # General checks for all Revocation entries
        operation = req.operation
        value_from_txn = operation.get(VALUE)
        issued_from_txn = value_from_txn.get(ISSUED, [])
        revoked_from_txn = value_from_txn.get(REVOKED, [])
        intersection = set(issued_from_txn).intersection(set(revoked_from_txn))
        if len(intersection) > 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Can not have an index in both "
                                       "'issued' and 'revoked' lists")
        prev_accum = value_from_txn.get(PREV_ACCUM, None)
        accum = value_from_txn.get(ACCUM, None)
        if prev_accum is not None and current_entry is None:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Got '{}': {} but there is no "
                                       "previous REVOC_REG_ENTRY".format(PREV_ACCUM,
                                                                         prev_accum))
        if current_entry is None:
            return None
        value_from_state = current_entry.get(VALUE)
        assert value_from_state
        current_accum = value_from_state.get(ACCUM)
        if current_accum != value_from_txn.get(PREV_ACCUM):
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "The current accumulator value: {} "
                                       "must be equal to the last accumulator "
                                       "value: {} in transaction".format(
                                           current_accum,
                                           value_from_state.get(PREV_ACCUM)))
        if len(issued_from_txn) == 0 and len(revoked_from_txn) == 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Got '{}' and '{}' but '{}' and '{}' lists are empty".format(
                                           PREV_ACCUM, ACCUM,
                                           ISSUED, REVOKED))
        if prev_accum == accum and (len(issued_from_txn) > 0 or len(revoked_from_txn) > 0):
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Got equal accum and prev_accum but "
                                       "issued and revoked indices are not empty")

        # Do strategy specific validation
        self.specific_validation(current_entry, req)

    def set_to_state(self, txn):
        # Set REVOC_REG_ENTRY
        path, value_bytes = domain.prepare_revoc_reg_entry_for_state(txn)
        self.state.set(path, value_bytes)
        # Set ACCUM from REVOC_REG_ENTRY
        txn_data = get_payload_data(txn)
        txn_data[VALUE] = {ACCUM: txn_data[VALUE][ACCUM]}
        path, value_bytes = domain.prepare_revoc_reg_entry_accum_for_state(txn)
        self.state.set(path, value_bytes)

    @abstractmethod
    def specific_validation(self, current_entry, req: Request):
        raise NotImplementedError

    @abstractmethod
    def write(self, current_reg_entry, txn):
        raise NotImplementedError

    @staticmethod
    def get_delta(to_dict, from_dict=None):
        raise NotImplementedError


class RevokedStrategy(RevocationStrategy):
    # This strategy save in state only revoked indices

    def specific_validation(self, current_reg_entry, req: Request):
        value_from_state = current_reg_entry.get(VALUE)
        assert value_from_state
        indices = value_from_state.get(REVOKED, [])
        value_from_txn = req.operation.get(VALUE)
        issued_from_txn = value_from_txn.get(ISSUED, [])
        revoked_from_txn = value_from_txn.get(REVOKED, [])
        issued_difference = set(issued_from_txn).difference(indices)
        if len(issued_difference) > 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Issued indices from txn: {} "
                                       "are not present in the current "
                                       "revoked list from state: {}".format(issued_difference,
                                                                            indices))
        revoked_intersection = set(indices).intersection(revoked_from_txn)
        if len(revoked_intersection) > 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Revoked indices from txn: {} "
                                       "are already revoked "
                                       "in current state: {}".format(revoked_intersection,
                                                                     indices))

    def write(self, current_reg_entry, txn):
        txn = deepcopy(txn)
        txn_data = get_payload_data(txn)
        self.set_parameters_from_txn(author_did=get_from(txn),
                                     revoc_reg_def_id=txn_data.get(REVOC_REG_DEF_ID),
                                     req_id=get_req_id(txn))
        if current_reg_entry is not None:
            value_from_state = current_reg_entry.get(VALUE)
            assert value_from_state
            indices = value_from_state.get(REVOKED, [])
            value_from_txn = txn_data.get(VALUE)
            issued_from_txn = value_from_txn.get(ISSUED, [])
            revoked_from_txn = value_from_txn.get(REVOKED, [])
            # set with all previous revoked minus issued from txn
            result_indicies = set(indices).difference(issued_from_txn)
            result_indicies.update(revoked_from_txn)
            value_from_txn[ISSUED] = []
            value_from_txn[REVOKED] = list(result_indicies)
            txn_data[VALUE] = value_from_txn
        # contains already changed txn
        self.set_to_state(txn)
        del txn

    @staticmethod
    def get_delta(to_dict, from_dict=None):
        if from_dict is None:
            return to_dict[ISSUED], to_dict[REVOKED]
        revoked = set(to_dict[REVOKED]).difference(set(from_dict[REVOKED]))
        issued = set(from_dict[REVOKED]).difference(set(to_dict[REVOKED]))
        return issued, revoked


class IssuedStrategy(RevocationStrategy):
    # This strategy saves in state only issued indices

    def specific_validation(self, current_reg_entry, req: Request):
        value_from_state = current_reg_entry.get(VALUE)
        assert value_from_state
        indices = value_from_state.get(ISSUED, [])
        value_from_txn = req.operation.get(VALUE)
        issued_from_txn = value_from_txn.get(ISSUED, [])
        revoked_from_txn = value_from_txn.get(REVOKED, [])
        revoked_difference = set(revoked_from_txn).difference(indices)
        if len(revoked_difference) > 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Revoked indices from txn: {} "
                                       "are not present in the current "
                                       "issued list from state: {}".format(revoked_difference,
                                                                           indices))
        issued_intersection = set(indices).intersection(issued_from_txn)
        if len(issued_intersection) > 0:
            raise InvalidClientRequest(self.author_did,
                                       self.req_id,
                                       "Issued indices from txn: {} "
                                       "are already issued "
                                       "in current state: {}".format(issued_intersection,
                                                                     indices))

    def write(self, current_reg_entry, txn):
        txn = deepcopy(txn)
        txn_data = get_payload_data(txn)
        self.set_parameters_from_txn(author_did=get_from(txn),
                                     revoc_reg_def_id=txn_data.get(REVOC_REG_DEF_ID),
                                     req_id=get_req_id(txn))
        if current_reg_entry is not None:
            value_from_state = current_reg_entry.get(VALUE)
            assert value_from_state
            indices = value_from_state.get(ISSUED, [])
            value_from_txn = txn_data.get(VALUE)
            issued_from_txn = value_from_txn.get(ISSUED, [])
            revoked_from_txn = value_from_txn.get(REVOKED, [])
            # set with all previous issued minus revoked from txn
            result_indicies = set(indices).difference(revoked_from_txn)
            result_indicies.update(issued_from_txn)
            value_from_txn[REVOKED] = []
            value_from_txn[ISSUED] = list(result_indicies)
            txn_data[VALUE] = value_from_txn
        # contains already changed txn
        self.set_to_state(txn)
        del txn

    @staticmethod
    def get_delta(to_dict, from_dict=None):
        if from_dict is None:
            return to_dict[ISSUED], to_dict[REVOKED]
        issued = set(to_dict[ISSUED]).difference(set(from_dict[ISSUED]))
        revoked = set(from_dict[ISSUED]).difference(set(to_dict[ISSUED]))
        return issued, revoked
