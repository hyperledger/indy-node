from orderedset._orderedset import OrderedSet

from indy_node.server.plugin.agent_authz.helper import update_accumulator_val, \
    update_accumulator_with_multiple_vals
from storage.kv_store import KeyValueStorage
from stp_core.common.log import getlogger

logger = getlogger()


class DynamicAccumulator:
    """
    NAIVE AND INEFFICIENT DYNAMIC ACCUMULATOR
    """
    ACCUM_VLAUE_KEY_NAME = '__accum__'
    SIZE_KEY_NAME = '__size__'
    IDX_KEY_PREFIX = 'i:'
    COMM_KEY_PREFIX = 'c:'

    def __init__(self, generator, modulus, kv_store: KeyValueStorage):
        self.generator = generator
        self.modulus = modulus
        self.kv_store = kv_store
        self.committed_size = 0
        self.committed_value = generator
        self.uncommitted_value = self.committed_value
        # TODO: It feels cleaner to have a current batch's working set rather
        # than rely on the last member of the list
        self.uncommitted_additions = [OrderedSet(), ]
        self.uncommitted_deletions = [OrderedSet(), ]
        self.init_from_storage()

    def init_from_storage(self):
        try:
            v = self.kv_store.get(self.ACCUM_VLAUE_KEY_NAME)
            self.committed_value = int(v)
            self.uncommitted_value = self.committed_value
        except KeyError:
            pass
        try:
            s = self.kv_store.get(self.SIZE_KEY_NAME)
            self.committed_size = int(s)
        except KeyError:
            self.kv_store.put(self.SIZE_KEY_NAME, b'0')

    # ASSUMES COMMITMENT ADDITIONS/REMOVALS ARE DONE ONLY ONCE (NO DUPLICATE CHECK IS BEING PERFORMED)

    def add_commitment(self, commitment):
        self.uncommitted_additions[-1].add(commitment)
        self.uncommitted_value = update_accumulator_val(self.uncommitted_value, commitment, self.modulus)

    def remove_commitment(self, commitment):
        for uncommitteds in self.uncommitted_additions:
            # If commitment to remove is still uncommitted
            if commitment in uncommitteds:
                self.uncommitted_deletions[-1].add(commitment)

                # TODO: Fixme; TOO NAIVE, SHOULD BE OPTIMISED
                all_comms = OrderedSet()
                all_comms = self.add_remove_uncommitted_commitments(all_comms)

                self.uncommitted_value = update_accumulator_with_multiple_vals(
                    self.committed_value, all_comms, self.modulus)
                break
        else:
            # If commitment to remove has been committed
            if self.has_committed_commitment(commitment):
                self.uncommitted_deletions[-1].add(commitment)

                # TODO: Fixme; TOO NAIVE, SHOULD BE OPTIMISED
                # Get all committed commitments
                all_comms = self._get_all_committed_commitments()

                # Add and Remove any uncommitted commitments
                all_comms = self.add_remove_uncommitted_commitments(all_comms)

                self.uncommitted_value = update_accumulator_with_multiple_vals(
                    self.generator, all_comms, self.modulus)
            else:
                # TODO: Fixme; This is temporary
                # raise KeyError('Commitment to remove, {} not found anywhere', commitment)
                logger.error('{} got commitment to remove, {} not found anywhere', self, commitment)

    def add_remove_uncommitted_commitments(self, all_comms):
        for u in self.uncommitted_additions:
            all_comms = all_comms.union(u)
        for u in self.uncommitted_deletions:
            all_comms = all_comms.difference(u)
        return all_comms

    def commit(self):
        if not self.uncommitted_deletions[0]:
            logger.debug('{}, during commit, found 0 commitments to remove, '
                         '{} new commitments to add'.format(self,
                                                            len(self.uncommitted_additions[0])))
            # No removals
            if self.uncommitted_additions[0]:
                self.update_with_committed_commitments(self.uncommitted_additions[0])
        else:
            new_commitments_to_commit = self.uncommitted_additions[0].difference(
                self.uncommitted_deletions[0])
            if self.uncommitted_deletions[0].issubset(self.uncommitted_additions[0]):
                logger.debug(
                    '{}, during commit, found {} uncommitted commitments, 0 committed commitments to remove, '
                    '{} new commitments to add'.format(self, len(self.uncommitted_deletions[0]), len(new_commitments_to_commit)))
                # No committed removals
                self.update_with_committed_commitments(new_commitments_to_commit)
            else:
                # Committed removals
                all_comms = OrderedSet()

                all_comms.update(self._get_all_committed_commitments())

                # Add uncommitted additions
                all_comms = all_comms.union(self.uncommitted_additions[0])
                # Remove uncommitted deletions
                all_comms = all_comms.difference(self.uncommitted_deletions[0])

                # Recompute accumulated value
                self.committed_value = update_accumulator_with_multiple_vals(
                    self.generator, all_comms, self.modulus)

                # Remove committed commitments (excluding uncommitteds)
                to_remove = self.uncommitted_deletions[0].difference(self.uncommitted_additions[0])
                logger.debug(
                    '{}, during commit, {} committed commitments to remove, '
                    '{} new commitments to add'.format(self, len(to_remove),len(new_commitments_to_commit)))
                self.remove_committed_commitments(to_remove)

                self.add_committed_commitments(new_commitments_to_commit)
                self.committed_size += len(new_commitments_to_commit)

        self.kv_store.put(self.ACCUM_VLAUE_KEY_NAME, str(self.committed_value))
        self.kv_store.put(self.SIZE_KEY_NAME, str(self.committed_size))
        self.uncommitted_additions = self.uncommitted_additions[1:]
        self.uncommitted_deletions = self.uncommitted_deletions[1:]

    def update_with_committed_commitments(self, commitments):
        self.committed_value = update_accumulator_with_multiple_vals(
            self.committed_value, commitments,
            self.modulus)
        self.add_committed_commitments(commitments)
        self.committed_size += len(commitments)

    def has_committed_commitment(self, commitment):
        try:
            self.kv_store.get(self.commitment_key(commitment))
            return True
        except KeyError:
            return False

    def remove_committed_commitment(self, commitment):
        idx = self.kv_store.get(self.commitment_key(commitment))
        batch = [
            (self.kv_store.REMOVE_OP, self.commitment_key(commitment), str(idx)),
            (self.kv_store.REMOVE_OP, self.index_key(idx), str(commitment))
        ]
        self.kv_store.do_ops_in_batch(batch)

    def remove_committed_commitments(self, commitments):
        batch = []
        for commitment in commitments:
            idx = self.kv_store.get(self.commitment_key(commitment))
            batch.append((self.kv_store.REMOVE_OP, self.commitment_key(commitment), None))
            batch.append((self.kv_store.REMOVE_OP, self.index_key(idx), None))
        self.kv_store.do_ops_in_batch(batch)

    def add_committed_commitments(self, commitments):
        s = self.committed_size
        batch = []
        for commitment in commitments:
            batch.append((self.commitment_key(commitment), str(s+1)))
            batch.append((self.index_key(str(s+1)), str(commitment)))
            s += 1
        self.kv_store.setBatch(batch)

    def get_witness_data_for_committed_commitment(self, commitment):
        # Returns current committed accumulated value, accumulated value
        # prior to adding `commitment` and commitments added
        # after adding `commitment`
        if not self.has_committed_commitment(commitment):
            return None, None, None
        idx = int(self.kv_store.get(self.commitment_key(commitment)))
        commitments_before = []
        commitments_after = []
        if not isinstance(commitment, int):
            commitment = int(commitment)
        # Get all committed commitments and split them
        for i in range(1, self.committed_size + 1):
            try:
                c = self.kv_store.get(self.index_key(i))
                c = int(c.decode())
                if c == commitment:
                    continue
                if i > idx:
                    commitments_after.append(c)
                else:
                    commitments_before.append(c)
            except KeyError:
                continue
        return self.committed_value, update_accumulator_with_multiple_vals(
            self.generator, commitments_before, self.modulus), commitments_after

    def _get_all_committed_commitments(self):
        all_comms = OrderedSet()
        for i in range(1, self.committed_size + 1):
            try:
                c = self.kv_store.get(self.index_key(i))
                all_comms.add(int(c.decode()))
            except KeyError:
                continue
        return all_comms

    def new_batch_added(self):
        self.uncommitted_additions.append(OrderedSet())
        self.uncommitted_deletions.append(OrderedSet())

    def remove_last_batch(self):
        self.uncommitted_additions = self.uncommitted_additions[:-1]
        self.uncommitted_deletions = self.uncommitted_deletions[:-1]

        self.uncommitted_additions.append(OrderedSet())
        self.uncommitted_deletions.append(OrderedSet())

    @staticmethod
    def commitment_key(commitment):
        if isinstance(commitment, (bytearray, bytes)):
            commitment = str(int(commitment))
        return '{}{}'.format(DynamicAccumulator.COMM_KEY_PREFIX, commitment)

    @staticmethod
    def index_key(index):
        if isinstance(index, (bytearray, bytes)):
            index = str(int(index))
        return '{}{}'.format(DynamicAccumulator.IDX_KEY_PREFIX, index)
