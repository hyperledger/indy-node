import functools

import pytest

from indy_common.constants import POOL_UPGRADE
from indy_node.server.node import Node
from plenum.common.constants import FORCE, TXN_TYPE
from plenum.test.helper import sdk_gen_request
from plenum.test.primary_selection.test_view_changer_primary_selection import FakeNode


@pytest.fixture(scope='function')
def fake_node(tdir, tconf):
    node = FakeNode(tdir, config=tconf)
    node.unpackClientMsg = functools.partial(Node.unpackClientMsg, node)
    node.is_request_need_quorum = functools.partial(Node.is_request_need_quorum, node)
    node.master_replica._consensus_data.waiting_for_new_view = True
    fake_node.postToClientInBox = lambda a, b: None
    return node


def test_client_force_request_not_discard_in_view_change_with_dict(fake_node):
    sender = "frm"
    msg = sdk_gen_request({TXN_TYPE: POOL_UPGRADE, FORCE: True}).as_dict

    def post_to_client_in_box(received_msg, received_frm):
        assert received_frm == sender
        assert received_msg == msg
    fake_node.postToClientInBox = post_to_client_in_box

    def discard(received_msg, reason, logMethod, cliOutput):
        assert False, "Message {} was discard with '{}'".format(received_msg, reason)
    fake_node.discard = discard

    fake_node.unpackClientMsg(msg, sender)
