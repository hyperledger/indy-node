import asyncio
import functools
import json
import multiprocessing
import os
import socket
import subprocess
from datetime import datetime
from typing import List, Tuple

import dateutil.tz
from plenum.common.constants import TXN_TYPE, DATA, VERSION
from plenum.common.types import f
from plenum.common.util import randomString
from plenum.test import waits as plenumWaits
from plenum.test.helper import waitForSufficientRepliesForRequests
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

from indy_client.client.wallet.upgrade import Upgrade
from indy_common.constants import NODE_UPGRADE, ACTION, MESSAGE_TYPE, \
    RESTART_MESSAGE
from indy_common.config import controlServiceHost, controlServicePort
from indy_node.server.upgrade_log import UpgradeLog
from indy_node.server.upgrader import Upgrader
from indy_node.test.helper import TestNode
from indy_node.utils.node_control_tool import NodeControlTool
from indy_common.config_helper import NodeConfigHelper


logger = getlogger()


def compose_restart_message(action):
    return (json.dumps({MESSAGE_TYPE: RESTART_MESSAGE})).encode()


def send_restart_message(action):
    sock = socket.create_connection(
        (controlServiceHost, controlServicePort))
    sock.sendall(compose_restart_message(action))
    sock.close()


async def _createServer(host, port):
    """
    Create async server that listens host:port, reads client request and puts
    value to some future that can be used then for checks

    :return: reference to server and future for request
    """
    indicator = asyncio.Future()

    async def _handle(reader, writer):
        raw = await reader.readline()
        request = raw.decode("utf-8")
        indicator.set_result(request)
    server = await asyncio.start_server(_handle, host, port)
    return server, indicator


def _stopServer(server):
    print('Closing server')
    server.close()
    # def _stop(x):
    #     print('Closing server')
    #     server.close()
    # return _stop


def _checkFuture(future):
    """
    Wrapper for futures that lets checking of their status using 'eventually'
    """
    def _check():
        if future.cancelled():
            return None
        if future.done():
            return future.result()
        raise Exception()
    return _check

