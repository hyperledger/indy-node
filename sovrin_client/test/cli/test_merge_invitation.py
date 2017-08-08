import pytest

from sovrin_client.agent.agent_issuer import AgentIssuer
from sovrin_client.agent.agent_prover import AgentProver
from sovrin_client.agent.agent_verifier import AgentVerifier
from sovrin_client.agent.walleted import Walleted
from sovrin_client.client.wallet.connection import Connection
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.agent.walleted_agent import WalletedAgent
from plenum.common.constants import NAME, VERSION, ATTRIBUTES, VERIFIABLE_ATTRIBUTES


def test_merge_invitation():
    wallet1 = Wallet('wallet1')
    connection_1 = Connection('connection1')
    walleted_agent = WalletedAgent(name='wallet1')

    wallet1.addConnection(connection_1)
    walleted_agent.wallet = wallet1
    connection = walleted_agent._wallet.getConnection('connection1')
    assert len(connection.proofRequests) == 0
    request_data = {'connection-request': {'name': 'connection1'},
                    'proof-requests': [{NAME: 'proof1', VERSION: '1',
                                        ATTRIBUTES: {'att_key1': 'att_value1', 'att_key2': 'att_value2'},
                                        VERIFIABLE_ATTRIBUTES: {'ver_att_key1': 'ver_att_value1'}}]}
    walleted_agent._merge_request(request_data)
    assert len(connection.proofRequests) == 1
    assert len(connection.proofRequests[0].attributes.keys()) == 2
    assert connection.proofRequests[0].attributes['att_key1'] == 'att_value1'
