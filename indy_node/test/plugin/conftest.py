import pytest

from indy_client.test.helper import build_client_for_wallet
from indy_node.server.plugin.agent_authz.main import integrate_plugin_in_node
from indy_node.test.plugin.authz_wallet import AuthzWallet
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import randomString


@pytest.fixture(scope='module')
def agent1_wallet():
    # TODO: Use the indy-sdk wallet
    wallet = AuthzWallet('agent1')
    wallet.addIdentifier(signer=SimpleSigner())
    return wallet


@pytest.fixture(scope='module')
def agent1_client(nodeSet, agent1_wallet, looper, tdirWithClientPoolTxns):
    # TODO: Use the indy-sdk client
    return build_client_for_wallet(looper, tdirWithClientPoolTxns,
                                   agent1_wallet)


@pytest.fixture(scope='module')
def agent2_wallet():
    # TODO: Use the indy-sdk wallet
    wallet = AuthzWallet('agent2')
    wallet.addIdentifier(signer=SimpleSigner())
    return wallet


@pytest.fixture(scope='module')
def agent2_client(nodeSet, agent2_wallet, looper, tdirWithClientPoolTxns):
    # TODO: Use the indy-sdk client
    return build_client_for_wallet(looper, tdirWithClientPoolTxns, agent2_wallet)


@pytest.fixture(scope="module")
def do_post_node_creation():
    # Integrate plugin into each node.
    def _post_node_creation(node):
        integrate_plugin_in_node(node)

    return _post_node_creation


@pytest.fixture(scope="module")
def nodeSet(tconf, do_post_node_creation, txnPoolNodeSet):
    return txnPoolNodeSet


@pytest.fixture(scope='module')
def sdk_client_seed():
    return randomString(32)


@pytest.fixture(scope='module')
def query_wallet_client(sdk_client_seed, sdk_wallet_client, sdk_pool_handle):
    return sdk_wallet_client
