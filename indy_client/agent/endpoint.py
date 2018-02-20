import os

from typing import Callable

from plenum.common.message_processor import MessageProcessor

from stp_core.common.log import getlogger
from stp_core.network.auth_mode import AuthMode
from plenum.common.util import randomString
from stp_core.crypto.util import randomSeed
from stp_core.types import HA
from stp_zmq.simple_zstack import SimpleZStack

logger = getlogger()


class EndpointCore(MessageProcessor):

    def tracedMsgHandler(self, msg):
        logger.debug("Got {}".format(msg))
        self.msgHandler(msg)


class ZEndpoint(SimpleZStack, EndpointCore):
    def __init__(self, port: int, msgHandler: Callable,
                 name: str=None, basedirpath: str=None, seed=None,
                 onlyListener=False, msgRejectHandler=None):
        stackParams = {
            "name": name or randomString(8),
            "ha": HA("0.0.0.0", port),
            "auth_mode": AuthMode.ALLOW_ANY.value
        }
        if basedirpath:
            stackParams["basedirpath"] = os.path.join(basedirpath, "keys")

        seed = seed or randomSeed()
        SimpleZStack.__init__(
            self,
            stackParams,
            self.tracedMsgHandler,
            seed=seed,
            onlyListener=onlyListener,
            msgRejectHandler=msgRejectHandler)

        self.msgHandler = msgHandler
