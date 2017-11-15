from indy_client.client.wallet.connection import Connection
from indy_client.client.wallet.wallet import Wallet
from indy_client.agent.walleted_agent import WalletedAgent
from plenum.common.constants import NAME, VERSION, ATTRIBUTES, VERIFIABLE_ATTRIBUTES, NONCE


def test_merge_invitation():
    nonce = "12345"
    wallet1 = Wallet('wallet1')
    connection_1 = Connection('connection1')
    walleted_agent = WalletedAgent(name='wallet1')

    wallet1.addConnection(connection_1)
    walleted_agent.wallet = wallet1
    connection = walleted_agent._wallet.getConnection('connection1')
    assert len(connection.proofRequests) == 0
    request_data = {'connection-request': {NAME: 'connection1',
                                           NONCE: nonce},
                    'proof-requests': [{NAME: 'proof1',
                                        VERSION: '1',
                                        ATTRIBUTES: {'att_key1': 'att_value1',
                                                     'att_key2': 'att_value2'},
                                        VERIFIABLE_ATTRIBUTES: {'ver_att_key1': 'ver_att_value1'}}]}

    # test that a proof request with attributes can be merged into a connection
    # that already exists but has no proof requests.
    walleted_agent._merge_request(request_data)
    assert len(connection.proofRequests) == 1
    assert len(connection.proofRequests[0].attributes.keys()) == 2
    assert connection.proofRequests[0].attributes['att_key1'] == 'att_value1'

    request_data2 = {'connection-request': {NAME: 'connection1',
                                            NONCE: nonce},
                     'proof-requests': [{NAME: 'proof1',
                                         VERSION: '1',
                                         ATTRIBUTES: {'att_key1': 'att_value1',
                                                      'att_key2': 'att_value2',
                                                      'att_key3': 'att_value3'},
                                         VERIFIABLE_ATTRIBUTES: {'ver_att_key1': 'ver_att_value1',
                                                                 'ver_att_key2': 'ver_att_value2'},
                                         }]}

    # test that additional attributes and verifiable attributes can be
    # merged into an already existing proof request
    walleted_agent._merge_request(request_data2)
    assert len(connection.proofRequests) == 1
    assert len(connection.proofRequests[0].attributes.keys()) == 3
    assert connection.proofRequests[0].attributes['att_key3'] == 'att_value3'
    assert len(connection.proofRequests[0].verifiableAttributes.keys()) == 2

    request_data3 = {'connection-request': {NAME: 'connection1',
                                            NONCE: nonce},
                     'proof-requests': [{NAME: 'proof2',
                                         VERSION: '1',
                                         ATTRIBUTES: {'att_key1': 'att_value1',
                                                      'att_key2': 'att_value2',
                                                      'att_key3': 'att_value3'},
                                         VERIFIABLE_ATTRIBUTES: {'ver_att_key1': 'ver_att_value1',
                                                                 'ver_att_key2': 'ver_att_value2'},
                                         }]}

    # test that a second proof from the same connection can be merged
    walleted_agent._merge_request(request_data3)
    assert len(connection.proofRequests) == 2
    assert len(connection.proofRequests[1].attributes.keys()) == 3
    assert connection.proofRequests[1].attributes['att_key3'] == 'att_value3'
    assert len(connection.proofRequests[1].verifiableAttributes.keys()) == 2
