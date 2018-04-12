import asyncio

import multiprocessing

import time

from indy_common.constants import POOL_RESTART, RESTART_MESSAGE
from indy_node.test.pool_restart.helper import compose_restart_message, \
    send_restart_message
from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching

m = multiprocessing.Manager()
whitelist = ['Unexpected error in _restart test']


def test_node_control_tool_restart(looper, tdir, monkeypatch, tconf):
    received = m.list()
    msg = RESTART_MESSAGE
    stdout = 'teststdout'

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_process_data', received.append)

    def check_message():
        assert len(received) == 1
        assert received[0] == compose_restart_message(msg)

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        send_restart_message(msg)
        looper.run(eventually(check_message))
    finally:
        nct.stop()


def test_communication_with_node_control_tool(looper, tdir, tconf, monkeypatch):
    received = m.list()
    msg = RESTART_MESSAGE
    stdout = 'teststdout'

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_restart', restart_count)

    def check_restart_count():
        assert len(received) == 1

    def restart_count():
        received.append(RESTART_MESSAGE)

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        send_restart_message(msg)
        looper.run(eventually(check_restart_count))
    finally:
        nct.stop()
