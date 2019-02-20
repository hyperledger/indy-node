from plenum.common.constants import AUDIT_LEDGER_ID, POOL_LEDGER_ID, CONFIG_LEDGER_ID, DOMAIN_LEDGER_ID
from plenum.common.ledger_manager import LedgerManager
from plenum.server.pool_manager import TxnPoolManager


class LedgerCatchupHelper:

    LEDGER_IDS = [AUDIT_LEDGER_ID, POOL_LEDGER_ID, CONFIG_LEDGER_ID, DOMAIN_LEDGER_ID]

    def get_new_ledger_manager(self) -> LedgerManager:
        ledger_sync_order = self.LEDGER_IDS
        return LedgerManager(self, ownedByNode=True,
                             postAllLedgersCaughtUp=self.allLedgersCaughtUp,
                             preCatchupClbk=self.preLedgerCatchUp,
                             postCatchupClbk=self.postLedgerCatchUp,
                             ledger_sync_order=ledger_sync_order,
                             metrics=self.metrics)

    def init_ledger_manager(self):
        self._add_pool_ledger()
        self._add_config_ledger()
        self._add_domain_ledger()

    def on_new_ledger_added(self, ledger_id):
        # If a ledger was added after a replicas were created
        self.replicas.register_new_ledger(ledger_id)

    def _add_pool_ledger(self):
        self.ledgerManager.addLedger(
            POOL_LEDGER_ID,
            self.poolLedger,
            preCatchupStartClbk=self.prePoolLedgerCatchup,
            postCatchupCompleteClbk=self.postPoolLedgerCaughtUp,
            postTxnAddedToLedgerClbk=self.postTxnFromCatchupAddedToLedger)
        self.on_new_ledger_added(POOL_LEDGER_ID)

    def _add_domain_ledger(self):
        self.ledgerManager.addLedger(
            DOMAIN_LEDGER_ID,
            self.domainLedger,
            preCatchupStartClbk=self.preDomainLedgerCatchup,
            postCatchupCompleteClbk=self.postDomainLedgerCaughtUp,
            postTxnAddedToLedgerClbk=self.postTxnFromCatchupAddedToLedger)
        self.on_new_ledger_added(DOMAIN_LEDGER_ID)

    # TODO: should be renamed to `post_all_ledgers_caughtup`
    def allLedgersCaughtUp(self):
        if self.num_txns_caught_up_in_last_catchup() == 0:
            self.catchup_rounds_without_txns += 1
        last_caught_up_3PC = self.ledgerManager.last_caught_up_3PC
        master_last_ordered_3PC = self.master_last_ordered_3PC
        self.mode = Mode.synced
        for replica in self.replicas.values():
            replica.on_catch_up_finished(last_caught_up_3PC,
                                         master_last_ordered_3PC)
        logger.info('{}{} caught up till {}'
                    .format(CATCH_UP_PREFIX, self, last_caught_up_3PC),
                    extra={'cli': True})
        # Replica's messages should be processed right after unstashing because the node
        # may not need a new one catchup. But in case with processing 3pc messages in
        # next looper iteration, new catchup will have already begun and unstashed 3pc
        # messages will stash again.
        # TODO: Divide different catchup iterations for different looper iterations. And remove this call after.
        if self.view_change_in_progress:
            self._process_replica_messages()

        # TODO: Maybe a slight optimisation is to check result of
        # `self.num_txns_caught_up_in_last_catchup()`
        self.processStashedOrderedReqs()

        # More than one catchup may be needed during the current ViewChange protocol
        # TODO: separate view change and catchup logic
        if self.is_catchup_needed():
            logger.info('{} needs to catchup again'.format(self))
            self.start_catchup()
        else:
            logger.info('{}{} does not need any more catchups'
                        .format(CATCH_UP_PREFIX, self),
                        extra={'cli': True})
            self.no_more_catchups_needed()
            # select primaries after pool ledger caughtup
            if not self.view_change_in_progress:
                self.select_primaries()

    def postPoolLedgerCaughtUp(self, **kwargs):
        self.mode = Mode.discovered
        # The node might have discovered more nodes, so see if schedule
        # election if needed.
        if isinstance(self.poolManager, TxnPoolManager):
            self.checkInstances()

        # TODO: why we do it this way?
        # Initialising node id in case where node's information was not present
        # in pool ledger at the time of starting, happens when a non-genesis
        # node starts
        self.id

    def postDomainLedgerCaughtUp(self, **kwargs):
        """
        Process any stashed ordered requests and set the mode to
        `participating`
        :return:
        """
        pass

    def preLedgerCatchUp(self, ledger_id):
        # Process any Ordered requests. This causes less transactions to be
        # requested during catchup. Also commits any uncommitted state that
        # can be committed
        logger.info('{} going to process any ordered requests before starting catchup.'.format(self))
        self.force_process_ordered()
        self.processStashedOrderedReqs()

        # revert uncommitted txns and state for unordered requests
        r = self.master_replica.revert_unordered_batches()
        logger.info('{} reverted {} batches before starting catch up for ledger {}'.format(self, r, ledger_id))

    def postLedgerCatchUp(self, ledger_id, last_caughtup_3pc):
        # update 3PC key interval tree to return last ordered to other nodes in Ledger Status
        self._update_txn_seq_range_to_3phase_after_catchup(ledger_id, last_caughtup_3pc)

    def postTxnFromCatchupAddedToLedger(self, ledger_id: int, txn: Any):
        rh = self.postRecvTxnFromCatchup(ledger_id, txn)
        if rh:
            rh.updateState([txn], isCommitted=True)
            state = self.getState(ledger_id)
            state.commit(rootHash=state.headHash)
            if ledger_id == DOMAIN_LEDGER_ID and rh.ts_store:
                rh.ts_store.set(get_txn_time(txn),
                                state.headHash)
            logger.trace("{} added transaction with seqNo {} to ledger {} during catchup, state root {}"
                         .format(self, get_seq_no(txn), ledger_id,
                                 state_roots_serializer.serialize(bytes(state.committedHeadHash))))
        self.updateSeqNoMap([txn], ledger_id)
        self._clear_request_for_txn(ledger_id, txn)

    def _clear_request_for_txn(self, ledger_id, txn):
        req_key = get_digest(txn)
        if req_key is not None:
            self.master_replica.discard_req_key(ledger_id, req_key)
            reqState = self.requests.get(req_key, None)
            if reqState:
                if reqState.forwarded and not reqState.executed:
                    self.mark_request_as_executed(reqState.request)
                    self.requests.ordered_by_replica(reqState.request.key)
                    self.requests.free(reqState.request.key)
                    self.doneProcessingReq(req_key)
                if not reqState.forwarded:
                    self.requests.pop(req_key, None)
                    self._clean_req_from_verified(reqState.request)
                    self.doneProcessingReq(req_key)

    def postRecvTxnFromCatchup(self, ledgerId: int, txn: Any):
        if ledgerId == POOL_LEDGER_ID:
            self.poolManager.onPoolMembershipChange(txn)
        if ledgerId == DOMAIN_LEDGER_ID:
            self.post_txn_from_catchup_added_to_domain_ledger(txn)
        typ = get_type(txn)
        # Since a ledger can contain txns which can be processed by an arbitrary number of request handlers;
        # ledger-to-request_handler is a one-to-many relationship
        rh = self.get_req_handler(txn_type=typ)
        return rh