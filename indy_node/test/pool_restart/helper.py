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
from indy_common.constants import NODE_UPGRADE, ACTION
from indy_common.config import controlServiceHost, controlServicePort
from indy_node.server.upgrade_log import UpgradeLog
from indy_node.server.upgrader import Upgrader
from indy_node.test.helper import TestNode
from indy_node.utils.node_control_tool import NodeControlTool
from indy_common.config_helper import NodeConfigHelper


logger = getlogger()


def compose_restart_message(action):
    return (json.dumps({ACTION: action})).encode()


def send_restart_message(action):
    sock = socket.create_connection(
        (controlServiceHost, controlServicePort))
    sock.sendall(compose_restart_message(action))
    sock.close()
