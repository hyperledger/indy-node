import sys

try:
    from indy_client import *
except ImportError as e:
    print("Indy Client is required for this guild, "
          "see doc for installing Indy Client.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

try:
    from indy_node import *
except ImportError as e:
    print("Indy Node is required for this guild, "
          "see doc for installing Indy Node.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

from indy_client.test.agent.acme import create_acme, bootstrap_acme
from indy_client.test.agent.faber import create_faber, bootstrap_faber
from indy_client.test.agent.thrift import create_thrift, bootstrap_thrift
from indy_common.constants import TRUST_ANCHOR
from indy_common.identity import Identity

from indy_common.config_util import getConfig

from plenum.common.plugin_helper import loadPlugins
from indy_client.cli.cli import IndyCli
from indy_node.pool.local_pool import create_local_pool


def demo_start_agents(pool, looper, b_dir):
    demo_start_agent(b_dir, create_faber, bootstrap_faber,
                     pool.create_client(5500), looper, pool.steward_agent())

    demo_start_agent(b_dir, create_acme, bootstrap_acme,
                     pool.create_client(5501), looper, pool.steward_agent())

    demo_start_agent(b_dir, create_thrift, bootstrap_thrift,
                     pool.create_client(5502), looper, pool.steward_agent())


def demo_start_agent(b_dir, create_func, bootstrap_func,
                     client, looper, steward):
    looper.runFor(2)
    agent = create_func(base_dir_path=b_dir, client=client)

    steward.publish_trust_anchor(Identity(identifier=agent.wallet.defaultId,
                                          verkey=agent.wallet.getVerkey(
                                              agent.wallet.defaultId),
                                          role=TRUST_ANCHOR))
    looper.runFor(4)

    raw = '{"endpoint": {"ha": "127.0.0.1:' + str(agent.port) + '"}}'
    endpointAttrib = agent.wallet.build_attrib(agent.wallet.defaultId, raw=raw)
    agent.publish_trust_anchor_attribute(endpointAttrib)

    looper.runFor(4)

    looper.add(agent)

    looper.runFor(2)

    looper.run(bootstrap_func(agent))


def main():
    config = getConfig()
    base_dir = config.CLI_BASE_DIR
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    loadPlugins(base_dir)

    pool = create_local_pool(base_dir)

    demo_start_agents(pool, pool, pool.base_dir)

    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)

    cli = IndyCli(looper=pool,
                  basedirpath=pool.base_dir,
                  logFileName=logFilePath,
                  withNode=False)

    pool.run(cli.shell())


def start_getting_started():
    main()


if __name__ == "__main__":
    main()
