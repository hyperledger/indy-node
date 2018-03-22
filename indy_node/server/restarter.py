import os
from collections import deque
from datetime import datetime, timedelta
from functools import partial
from typing import Tuple, Union, Optional, Callable, Dict

import dateutil.parser
import dateutil.tz

from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE, VERSION, DATA, IDENTIFIER
from plenum.common.types import f
from plenum.server.has_action_queue import HasActionQueue
from indy_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, IN_PROGRESS, FORCE, \
    POOL_RESTART, RESTART
from plenum.server import notifier_plugin_manager
from ledger.util import F
import asyncio

logger = getlogger()


class Restarter(HasActionQueue):

    def __init__(self,
                 nodeId,
                 nodeName,
                 dataDir,
                 config,
                 ledger,
                 restart_failed_callback: Callable = None,
                 restart_start_callback: Callable = None):

        self.nodeId = nodeId
        self.nodeName = nodeName
        self.config = config
        self.dataDir = dataDir
        self.ledger = ledger
        self.scheduled_restart = None  # type: Tuple[str, int, str]
        self._notifier = notifier_plugin_manager.PluginManager()
        self._restartFailedCallback = \
            restart_failed_callback if restart_failed_callback else lambda: None
        self._restart_start_callback = \
            restart_start_callback if restart_start_callback else lambda: None

        self.retry_timeout = 5
        self.retry_limit = 3

        HasActionQueue.__init__(self)

    def __repr__(self):
        # Since nodeid can be null till pool ledger has not caught up
        return self.nodeId or ''

    def service(self):
        return self._serviceActions()

    def handleRestartTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_RESTART
        Can schedule to restart node

        :param txn:
        """
        logger.info("Node '{}' handles restart txn {}".format(
            self.nodeName, txn))
        action = txn[DATA][ACTION]
        restart_id = None
        if action == START:
            when = txn[DATA][SCHEDULE]
            if isinstance(when, str):
                when = dateutil.parser.parse(when)
            if self.scheduled_restart:
                self._schedule_restart(when, restart_id)
            self._call_restart_agent()

    def _schedule_restart(self,
                          when: Union[datetime, str],
                          restart_id) -> None:
        """
        Schedules node restart to a newer version

        :param when: restart time
        :param restart_id: restart identifier (req_id+seq_no) of a txn that started the restart
        """
        assert isinstance(when, (str, datetime))
        logger.info("{}'s restarter processing restart"
                    .format(self))
        if isinstance(when, str):
            when = dateutil.parser.parse(when)
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

        # self._notifier.sendMessageUponNodeRestarteScheduled(
        #     "Restart of node has been scheduled on {}".format(
        #         self.nodeName, when))
        # self._restartLog.appendScheduled(when, restart_id)

        call_agent = partial(self._call_restart_agent)
        delay = 0
        if now < when:
            delay = (when - now).total_seconds()
        self.scheduled_restart = (when, restart_id)
        self._schedule(call_agent, delay)

    def _call_restart_agent(self) -> None:
        """
        Callback which is called when restart time come.
        Writes restart record to restart log and asks
        node control service to perform restart

        :param when: restart time
        :param version: version to restart to
        """

        logger.info("{}'s restart calling agent for restart".format(self))
        self._restart_start_callback()
        self.scheduled_restart = None
        asyncio.ensure_future(self._send_update_request())

    async def _send_update_request(self):
        retry_limit = self.retry_limit
        while retry_limit:
            try:
                msg = RestartMessage(RESTART).toJson()
                logger.info("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.warning("Failed to communicate to control tool: {}"
                               .format(ex))
                asyncio.sleep(self.retry_timeout)
                retry_limit -= 1

    async def _open_connection_and_send(self, message: str):
        control_service_host = self.config.controlServiceHost
        control_service_port = self.config.controlServicePort
        msg_bytes = bytes(message, "utf-8")
        _, writer = await asyncio.open_connection(
            host=control_service_host,
            port=control_service_port
        )
        writer.write(msg_bytes)
        writer.close()


class RestartMessage:
    """
    Data structure that represents request for node update
    """

    def __init__(self, action: str):
        self.action = action

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
