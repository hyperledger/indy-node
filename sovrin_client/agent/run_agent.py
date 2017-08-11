import os
import sys

from plenum.common.exceptions import NoConsensusYet
from stp_core.common.log import getlogger
from sovrin_client.agent.agent_cli import AgentCli

from stp_core.loop.looper import Looper

logger = getlogger()

async def runBootstrap(bootstrapFunc):
    try:
        await bootstrapFunc
    except TimeoutError as exc:
        raise NoConsensusYet("consensus is not yet achieved, "
                             "check if sovrin is running and "
                             "client is able to connect to it") from exc


def bootstrapAgentCli(name, agent, looper, bootstrap, config):
    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)
    cli = AgentCli(name='{}-Agent'.format(name).lower().replace(" ", "-"),
                   agentCreator=True,
                   agent=agent,
                   basedirpath=config.baseDir,
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
        agentCli = bootstrapAgentCli(agent.name, agent, looper, bootstrap, config)
        commands = sys.argv[1:]
        looper.run(agentCli.shell(*commands))

    if looper:
        run(looper)
    else:
        with Looper(debug=False) as looper:
            run(looper)


def runAgent(agent, looper=None, bootstrap=None):
    assert agent

    def do_run(looper):
        agent.loop = looper.loop
        looper.add(agent)
        logger.info("Running {} now (port: {})".format(agent.name, agent.port))
        if bootstrap:
            looper.run(runBootstrap(bootstrap))

    if looper:
        do_run(looper)
    else:
        with Looper(debug=True, loop=agent.loop) as looper:
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