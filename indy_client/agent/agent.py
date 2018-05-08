import asyncio
import os
from typing import Tuple

from plenum.common.motor import Motor
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.startable import Status
from plenum.common.types import HA
from plenum.common.util import randomString
from indy_client.agent.agent_net import AgentNet
from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet

from indy_common.config import agentLoggingLevel
from indy_common.config_util import getConfig
from indy_common.identity import Identity
from indy_common.strict_types import strict_types, decClassMethods

from stp_core.common.log import getlogger
from stp_core.network.port_dispenser import genHa
from stp_core.network.util import checkPortAvailable
from stp_core.types import Identifier

logger = getlogger()
logger.setLevel(agentLoggingLevel)


@decClassMethods(strict_types())
class Agent(Motor, AgentNet):
    def __init__(self,
                 name: str=None,
                 basedirpath: str=None,
                 client: Client=None,
                 port: int=None,
                 loop=None,
                 config=None,
                 endpointArgs=None):

        self.endpoint = None
        if port:
            checkPortAvailable(HA("0.0.0.0", port))
        Motor.__init__(self)
        self.loop = loop or asyncio.get_event_loop()
        self._eventListeners = {}  # Dict[str, set(Callable)]
        self._name = name or 'Agent'
        self._port = port

        self.config = config or getConfig()
        self.basedirpath = basedirpath or os.path.expanduser(
            self.config.CLI_BASE_DIR)
        self.endpointArgs = endpointArgs

        # Client used to connect to Indy and forward on owner's txns
        self._client = client  # type: Client

        # known identifiers of this agent's owner
        self.ownerIdentifiers = {}  # type: Dict[Identifier, Identity]

        self.logger = logger

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def name(self):
        return self._name

    @property
    def port(self):
        return self._port

    async def prod(self, limit) -> int:
        c = 0
        if self.get_status() == Status.starting:
            self.status = Status.started
            c += 1
        if self.client:
            c += await self.client.prod(limit)
        if self.endpoint:
            c += await self.endpoint.service(limit)
        return c

    def start(self, loop):
        AgentNet.__init__(self,
                          name=self._name.replace(" ", ""),
                          port=self._port,
                          basedirpath=self.basedirpath,
                          msgHandler=self.handleEndpointMessage,
                          config=self.config,
                          endpoint_args=self.endpointArgs)

        super().start(loop)
        if self.client:
            self.client.start(loop)
        if self.endpoint:
            self.endpoint.start()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        if self.client:
            self.client.stop()
        if self.endpoint:
            self.endpoint.stop()

    def _statusChanged(self, old, new):
        pass

    def onStopping(self, *args, **kwargs):
        pass

    def connect(self, network: str):
        """
        Uses the client to connect to Indy
        :param network: (test|live)
        :return:
        """
        raise NotImplementedError

    def syncKeys(self):
        """
        Iterates through ownerIdentifiers and ensures the keys are correct
        according to Indy. Updates the updated
        :return:
        """
        raise NotImplementedError

    def handleOwnerRequest(self, request):
        """
        Consumes an owner request, verifies it's authentic (by checking against
        synced owner identifiers' keys), and handles it.
        :param request:
        :return:
        """
        raise NotImplementedError

    def handleEndpointMessage(self, msg):
        raise NotImplementedError

    def ensureConnectedToDest(self, name, ha, clbk, *args):
        if self.endpoint.isConnectedTo(name=name, ha=ha):
            if clbk:
                clbk(*args)
        else:
            self.loop.call_later(.2, self.ensureConnectedToDest,
                                 name, ha, clbk, *args)

    def sendMessage(self, msg, name: str = None, ha: Tuple = None):

        def _send(msg):
            nonlocal name, ha
            self.endpoint.send(msg, name, ha)
            logger.debug("Message sent (to -> {}): {}".format(ha, msg))

        # TODO: if we call following isConnectedTo method by ha,
        # there was a case it found more than one remote, so for now,
        # I have changed it to call by remote name (which I am not sure
        # fixes the issue), need to come back to this.
        if not self.endpoint.isConnectedTo(name=name, ha=ha):
            self.ensureConnectedToDest(name, ha, _send, msg)
        else:
            _send(msg)

    def registerEventListener(self, eventName, listener):
        cur = self._eventListeners.get(eventName)
        if cur:
            self._eventListeners[eventName] = cur.add(listener)
        else:
            self._eventListeners[eventName] = {listener}

    def deregisterEventListener(self, eventName, listener):
        cur = self._eventListeners.get(eventName)
        if cur:
            self._eventListeners[eventName] = cur - set(listener)


def createAgent(agentClass, name, wallet=None, basedirpath=None, port=None,
                loop=None, clientClass=Client):
    config = getConfig()

    if not wallet:
        wallet = Wallet(name)
        wallet.addIdentifier(signer=DidSigner(
            seed=randomString(32).encode('utf-8')))
    if not basedirpath:
        basedirpath = config.CLI_BASE_DIR
    if not port:
        _, port = genHa()

    client = create_client(base_dir_path=basedirpath, client_class=clientClass)

    return agentClass(basedirpath=basedirpath,
                      client=client,
                      wallet=wallet,
                      port=port,
                      loop=loop)


def create_client(base_dir_path=None, client_class=Client):
    config = getConfig()

    if not base_dir_path:
        base_dir_path = config.CLI_BASE_DIR

    _, clientPort = genHa()
    client = client_class(randomString(6),
                          ha=("0.0.0.0", clientPort),
                          basedirpath=base_dir_path)
    return client
