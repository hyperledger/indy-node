import sys
import argparse

from indy_client.agent.agent import Agent
from indy_client.agent.run_agent import runAgentCli, runAgent
from stp_core.common.log import getlogger
from plenum.common.util import getFormattedErrorMsg
from indy_common.config_util import getConfig

logger = getlogger()


class RunnableAgent:
    @classmethod
    def get_passed_args(cls):
        return cls.parser_cmd_args()

    @classmethod
    def parser_cmd_args(cls):
        args = []
        if sys.stdin.isatty():
            args = sys.argv[1:]

        parser = argparse.ArgumentParser(
            description="Starts agents with given port, cred def and issuer seq")

        parser.add_argument('--port', type=int, required=False,
                            help='port where agent will listen')

        parser.add_argument('--withcli',
                            help='if given, agent will start in cli mode',
                            action='store_true')

        parser.add_argument('--network', required=False,
                            help='network connect to (sandbox by default)')

        args = parser.parse_args(args=args)
        # port = int(args.port) if args.port else None
        return args

    @classmethod
    def run_agent(cls, agent: Agent, looper=None,
                  bootstrap=None, with_cli=False):
        try:
            config = getConfig()
            if with_cli:
                runAgentCli(agent, config, looper=looper, bootstrap=bootstrap)
            else:
                runAgent(agent, looper, bootstrap)
            return agent
        except Exception as exc:
            error = "Agent startup failed: [cause : {}]".format(str(exc))
            logger.error(getFormattedErrorMsg(error))
