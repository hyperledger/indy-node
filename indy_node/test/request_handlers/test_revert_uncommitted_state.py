import functools
import time

import pytest

from indy_common.constants import CONFIG_LEDGER_ID
from indy_common.state import config
from indy_node.test.request_handlers.test_update_state_config_req_handler import prepare_request
from plenum.server.replica import Replica
from plenum.test.testing_utils import FakeSomething


@pytest.fixture
def fake_replica(config_ledger,
                 config_state):
    replica = FakeSomething(
        node=FakeSomething(getLedger=lambda *args, **kwargs: config_ledger,
                           getState=lambda *args, **kwargs: config_state,
                           onBatchRejected=lambda *args, **kwargs: True),
        logger=FakeSomething(info=lambda *args, **kwargs: True)
    )
    replica.revert = functools.partial(Replica.revert, replica)
    return replica


def test_revert_uncommitted_state(write_manager,
                                  db_manager,
                                  constraint_serializer,
                                  prepare_request,
                                  fake_replica,
                                  tmpdir_factory):
    action, constraint, request = prepare_request
    req_count = 1

    state_root_hash_before = db_manager.get_state(CONFIG_LEDGER_ID).headHash

    write_manager.apply_request(request, int(time.time()))
    """
    Check, that request exist in uncommitted state
    """
    from_state = db_manager.get_state(CONFIG_LEDGER_ID).get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint

    fake_replica.revert(CONFIG_LEDGER_ID,
                        state_root_hash_before,
                        req_count)
    """
    Txn is reverted from ledger and state
    """
    assert len(db_manager.get_ledger(CONFIG_LEDGER_ID).uncommittedTxns) == 0
    from_state = db_manager.get_state(CONFIG_LEDGER_ID).get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert from_state is None