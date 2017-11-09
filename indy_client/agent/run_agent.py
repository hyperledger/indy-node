import os
import sys

from indy_common.exceptions import NotConnectedToNetwork
from plenum.common.exceptions import NoConsensusYet
from stp_core.common.log import getlogger
from indy_client.agent.agent_cli import AgentCli
from indy_common.config_util import getConfig

from stp_core.loop.looper import Looper

logger = getlogger()


async def runBootstrap(bootstrapFunc):
    try:
        await bootstrapFunc
    except TimeoutError as exc:
        raise NoConsensusYet("consensus is not yet achieved, "
                             "check if indy is running and "
                             "client is able to connect to it") from exc


def bootstrapAgentCli(name, agent, looper, bootstrap, config):
    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)
    cli = AgentCli(name='{}-Agent'.format(name).lower().replace(" ", "-"),
                   agentCreator=True,
                   agent=agent,
                   basedirpath=config.CLI_BASE_DIR,
                   logFileName=logFilePath,
                   looper=looper)
    if bootstrap:
        try:
            looper.run(runBootstrap(bootstrap))
        except Exception as exc:
            error = "Agent startup failed: [cause : {}]".format(str(exc))
            cli.print(error)

    return cli


def runAgentCli(agent, config, looper=None, bootstrap=None):
    def run(looper):
        agent.loop = looper.loop
        logger.info("Running {} now (port: {})".format(agent.name, agent.port))
        agentCli = bootstrapAgentCli(
            agent.name, agent, looper, bootstrap, config)
        commands = sys.argv[1:]
        looper.run(agentCli.shell(*commands))

    if looper:
        run(looper)
    else:
        with Looper(debug=config.LOOPER_DEBUG) as looper:
            run(looper)


CONNECTION_TIMEOUT = 120


def runAgent(agent, looper=None, bootstrap=None):
    assert agent

    def is_connected(agent):
        client = agent.client
        if (client.mode is None) or (not client.can_send_write_requests()):
            raise NotConnectedToNetwork("Client hasn't finished catch-up with Pool Ledger yet or "
                                        "doesn't have sufficient number of connections")

    async def wait_until_connected(agent):
        from stp_core.loop.eventually import eventually
        await eventually(is_connected, agent,
                         timeout=CONNECTION_TIMEOUT, retryWait=2)

    def do_run(looper):
        agent.loop = looper.loop
        looper.add(agent)
        logger.info("Running {} now (port: {})".format(agent.name, agent.port))
        if bootstrap:
            looper.run(wait_until_connected(agent))
            looper.run(runBootstrap(bootstrap))

    if looper:
        do_run(looper)
    else:
        with Looper(debug=getConfig().LOOPER_DEBUG, loop=agent.loop) as looper:
            do_run(looper)
            looper.run()

# Note: Commented it as didn't find any usage of this method
# def run_agent(looper, wallet, agent):
#
#     def run():
#         _agent = agent
#         wallet.pendSyncRequests()
#         prepared = wallet.preparePending()
#         _agent.client.submitReqs(*prepared)
#
#         runAgent(_agent, looper)
#
#         return _agent, wallet
#
#     return run
