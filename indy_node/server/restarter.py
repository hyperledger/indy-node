import os
from datetime import datetime
from functools import partial
from typing import Union

import dateutil.parser
import dateutil.tz

from indy_common.types import Request
from indy_node.server.node_maintainer import NodeMaintainer, \
    NodeControlToolMessage
from indy_node.server.restart_log import RestartLogData, RestartLog
from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE
from indy_common.constants import ACTION, POOL_RESTART, START, DATETIME, \
    CANCEL, TIMEOUT, RESTART_MESSAGE
import asyncio

logger = getlogger()


class Restarter(NodeMaintainer):

    def _defaultLog(self, dataDir, config):
        log = os.path.join(dataDir, config.restartLogFile)
        return RestartLog(file_path=log)

    def _is_action_started(self):
        last_action = self.lastActionEventInfo
        if not last_action:
            logger.debug('Node {} has no restart events'
                         .format(self.nodeName))
            return False

        if last_action.ev_type != RestartLog.Events.started:
            logger.info(
                "Restart for node {} was not scheduled. Last event is {}"
                .format(self.nodeName, last_action))
            return False

        return True

    def _update_action_log_for_started_action(self):
        self._actionLog.append_succeeded(self.lastActionEventInfo.data)
        logger.info("Node '{}' successfully restarted"
                    .format(self.nodeName))

    def handleRestartRequest(self, req: Request) -> None:
        """
        Handles transaction of type POOL_RESTART
        Can schedule or cancel restart to a newer
        version at specified time

        :param req:
        """
        txn = req.operation
        if txn[TXN_TYPE] != POOL_RESTART:
            return

        action = txn[ACTION]
        if action == START:
            when = dateutil.parser.parse(txn[DATETIME]) \
                if DATETIME in txn.keys() and txn[DATETIME] not in ["0", "", None] \
                else None
            fail_timeout = txn.get(TIMEOUT, self.defaultActionTimeout)
            self.requestRestart(when, fail_timeout)
            return

        if action == CANCEL:
            if self.scheduledAction:
                self._cancelScheduledRestart()
                logger.info("Node '{}' cancels restart".format(
                    self.nodeName))
            return

        logger.error(
            "Got {} transaction with unsupported action {}".format(
                POOL_RESTART, action))

    def requestRestart(self, when=None, fail_timeout=None):
        if self.scheduledAction:
            if self.scheduledAction.when == when:
                logger.debug(
                    "Node {} already scheduled restart".format(
                        self.nodeName))
                return
            else:
                logger.info(
                    "Node '{}' cancels previous restart and schedules a new one".format(
                        self.nodeName))
                self._cancelScheduledRestart()

        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        if when is None or now >= when:
            msg = RestartMessage().toJson()
            try:
                asyncio.ensure_future(self._open_connection_and_send(msg))
            except Exception as ex:
                logger.warning(ex.args[0])
            return

        if fail_timeout is None:
            fail_timeout = self.defaultActionTimeout
        logger.info("Node '{}' schedules restart".format(
            self.nodeName))

        self._scheduleRestart(when, fail_timeout)

    def _scheduleRestart(self,
                         when: Union[datetime, str],
                         failTimeout) -> None:
        """
        Schedules node restart to a newer version

        :param version: version to restart to
        :param when: restart time
        """
        logger.info("{}'s restarter processing restart"
                    .format(self))
        if isinstance(when, str):
            when = dateutil.parser.parse(when)
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

        logger.info(
            "Restart of node '{}' has been scheduled on {}".format(
                self.nodeName, when))

        ev_data = RestartLogData(when)
        self._actionLog.append_scheduled(ev_data)

        callAgent = partial(self._callRestartAgent, ev_data,
                            failTimeout)
        delay = 0
        if now < when:
            delay = (when - now).total_seconds()
        self.scheduledAction = ev_data
        self._schedule(callAgent, delay)

    def _cancelScheduledRestart(self, justification=None) -> None:
        """
        Cancels scheduled restart

        :param when: time restart was scheduled to
        :param version: version restart scheduled for
        """

        if self.scheduledAction:
            why_prefix = ": "
            why = justification
            if justification is None:
                why_prefix = ", "
                why = "cancellation reason not specified"

            ev_data = self.scheduledAction
            logger.info("Cancelling restart"
                        " of node {}"
                        " scheduled on {}"
                        "{}{}"
                        .format(self.nodeName,
                                ev_data.when,
                                why_prefix,
                                why))

            self._unscheduleAction()
            self._actionLog.append_cancelled(ev_data)
            logger.info(
                "Restart of node '{}'"
                "has been cancelled due to {}".format(
                    self.nodeName, why))

    def _callRestartAgent(self, ev_data: RestartLogData, failTimeout) -> None:
        """
        Callback which is called when restart time come.
        Writes restart record to restart log and asks
        node control service to perform restart

        :param ev_data: restart event data
        :param version: version to restart to
        """

        logger.info("{}'s restart calling agent for restart".format(self))
        self._actionLog.append_started(ev_data)
        self._action_start_callback()
        self.scheduledAction = None
        asyncio.ensure_future(
            self._sendUpdateRequest(ev_data, failTimeout))

    async def _sendUpdateRequest(self, ev_data: RestartLogData, failTimeout):
        retryLimit = self.retry_limit
        while retryLimit:
            try:
                msg = RestartMessage().toJson()
                logger.info("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.warning("Failed to communicate to control tool: {}"
                               .format(ex))
                asyncio.sleep(self.retry_timeout)
                retryLimit -= 1
        if not retryLimit:
            self._action_failed(ev_data,
                                reason="problems in communication with "
                                       "node control service")
            self._unscheduleAction()
            self._actionFailedCallback()
        else:
            logger.info("Waiting {} minutes for restart to be performed"
                        .format(failTimeout))
            timesUp = partial(self._declareTimeoutExceeded, ev_data)
            self._schedule(timesUp, self.get_timeout(failTimeout))

    def _declareTimeoutExceeded(self, ev_data: RestartLogData):
        """
        This function is called when time for restart is up
        """
        logger.info("Timeout exceeded for {}".format(ev_data.when))
        last = self._actionLog.last_event
        if (last and last.ev_type == RestartLog.Events.failed and last.data == ev_data):
            return None

        self._action_failed(ev_data,
                            reason="exceeded restart timeout")

        self._unscheduleAction()
        self._actionFailedCallback()

    def _action_failed(self, *,
                       ev_data: RestartLogData,
                       reason=None,
                       external_reason=False):
        if reason is None:
            reason = "unknown reason"
        error_message = "Node {} failed restart" \
                        "scheduled on {} " \
                        "because of {}" \
            .format(self.nodeName,
                    ev_data.when,
                    reason)
        logger.error(error_message)
        if external_reason:
            logger.error("This problem may have external reasons, "
                         "check syslog for more information")


class RestartMessage(NodeControlToolMessage):
    """
    Data structure that represents request for node update
    """

    def __init__(self):
        super().__init__(RESTART_MESSAGE)

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
