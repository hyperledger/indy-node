import os
import shutil

from indy_client.agent.walleted_agent import WalletedAgent
from indy_client.anon_creds.indy_issuer import IndyIssuerWalletInMemory
from indy_client.anon_creds.indy_public_repo import IndyPublicRepo
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.client.TestClient import TestClient
from stp_core.network.port_dispenser import genHa


def test_restore_agent_wallets_from_minimal_go_live(tconf, tdirWithClientPoolTxns):
    source_dir = os.path.dirname(os.path.realpath(__file__))
    agent_wallet_source_path = os.path.join(
        source_dir, 'agent_wallet_from_minimal_go_live')
    issuer_wallet_source_path = os.path.join(
        source_dir, 'issuer_wallet_from_minimal_go_live')

    agent_wallets_dir = os.path.join(tconf.CLI_BASE_DIR, tconf.walletsDir,
                                     'agents', 'test-agent')
    issuer_wallet_dir = os.path.join(agent_wallets_dir, 'issuer')

    os.makedirs(issuer_wallet_dir)
    shutil.copy(agent_wallet_source_path,
                os.path.join(agent_wallets_dir, 'default.wallet'))
    shutil.copy(issuer_wallet_source_path,
                os.path.join(issuer_wallet_dir, 'issuer.wallet'))

    client = TestClient('test-client',
                        ha=genHa(),
                        basedirpath=tdirWithClientPoolTxns)
    agent = WalletedAgent('test-agent',
                          basedirpath=tdirWithClientPoolTxns,
                          client=client)

    agent_wallet = agent.wallet
    assert isinstance(agent_wallet, Wallet)

    agent_connections = agent_wallet.getConnectionNames()
    assert len(agent_connections) == 3
    assert 'Acme Corp' in agent_connections
    assert 'Faber College' in agent_connections
    assert 'Thrift Bank' in agent_connections

    issuer_wallet = agent.issuer.wallet
    assert isinstance(issuer_wallet, IndyIssuerWalletInMemory)
    assert isinstance(issuer_wallet._repo, IndyPublicRepo)
    assert isinstance(issuer_wallet._repo.wallet, Wallet)

    issuer_connections = issuer_wallet._repo.wallet.getConnectionNames()
    assert len(issuer_connections) == 3
    assert 'Acme Corp' in issuer_connections
    assert 'Faber College' in issuer_connections
    assert 'Thrift Bank' in issuer_connections
