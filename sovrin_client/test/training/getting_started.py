import sys

try:
    from sovrin_client import *
except ImportError as e:
    print("Sovrin Client is required for this guild, "
          "see doc for installing Sovrin Client.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

try:
    from sovrin_node import *
except ImportError as e:
    print("Sovrin Node is required for this guild, "
          "see doc for installing Sovrin Node.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

from sovrin_client.test.agent.acme import create_acme, bootstrap_acme
from sovrin_client.test.agent.faber import create_faber, bootstrap_faber
from sovrin_client.test.agent.thrift import create_thrift, bootstrap_thrift
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_common.identity import Identity

from sovrin_common.config_util import getConfig

from plenum.common.plugin_helper import loadPlugins
from sovrin_client.cli.cli import SovrinCli
from sovrin_node.pool.local_pool import create_local_pool

config = getConfig()


def demo_start_agents(pool, looper, b_dir):
    demo_start_agent(b_dir, create_faber, bootstrap_faber, pool.create_client(5500), looper, pool.steward_agent())

    demo_start_agent(b_dir, create_acme, bootstrap_acme, pool.create_client(5501), looper, pool.steward_agent())

    demo_start_agent(b_dir, create_thrift, bootstrap_thrift, pool.create_client(5502), looper, pool.steward_agent())


def demo_start_agent(b_dir, create_func, bootstrap_func, client, looper, steward):
    looper.runFor(2)
    agent = create_func(base_dir_path=b_dir, client=client)

    steward.publish_trust_anchor(Identity(identifier=agent.wallet.defaultId,
                                          verkey=agent.wallet.getVerkey(agent.wallet.defaultId),
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
    base_dir = config.baseDir
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    loadPlugins(base_dir)

    pool = create_local_pool(base_dir)

    demo_start_agents(pool, pool, pool.base_dir)

    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)

    cli = SovrinCli(looper=pool,
                    basedirpath=pool.base_dir,
                    logFileName=logFilePath,
                    withNode=False)

    pool.run(cli.shell())


def start_getting_started():
    main()


if __name__ == "__main__":
    main()
