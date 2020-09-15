import json
import pytest

from plenum.common.constants import NODE_IP, NODE_PORT, CLIENT_IP, CLIENT_PORT, ALIAS, VALIDATOR, SERVICES
from plenum.common.util import cryptonymToHex, hexToFriendly
from plenum.common.exceptions import RequestNackedException, RequestRejectedException

from plenum.test.helper import sdk_get_and_check_replies, sdk_get_bad_response, sdk_sign_request_strings, \
    sdk_send_signed_requests
from plenum.test.pool_transactions.helper import sdk_add_new_nym, prepare_node_request, \
    sdk_sign_and_send_prepared_request


@pytest.fixture(scope='function')
def node_request(looper, sdk_node_theta_added):
    sdk_steward_wallet, node = sdk_node_theta_added
    node_dest = hexToFriendly(node.nodestack.verhex)
    wh, did = sdk_steward_wallet
    node_request = looper.loop.run_until_complete(
        prepare_node_request(did, node.name, destination=node_dest,
                             nodeIp=node.nodestack.ha[0],
                             nodePort=node.nodestack.ha[1],
                             clientIp=node.clientstack.ha[0],
                             clientPort=node.clientstack.ha[1]))
    return json.loads(node_request)


def ensurePoolIsOperable(looper, sdk_pool_handle, sdk_wallet_creator):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_creator)


@pytest.mark.node_txn
def test_send_node_fails_if_dest_is_short_readable_name(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['dest'] = 'TheNewNode'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'b58 decoded value length 8 should be one of [16, 32]')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_dest_is_hex_key(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['dest'] = cryptonymToHex(
        node_request['operation']['dest']).decode() + "0"
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'should not contain the following chars')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_has_invalid_syntax_if_dest_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['dest'] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'b58 decoded value length 0 should be one of [16, 32]')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_has_invalid_syntax_if_dest_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['dest']
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields - dest')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_ip_contains_leading_space(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = ' 122.62.52.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_ip_contains_trailing_space(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = '122.62.52.13 '
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))

    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_ip_has_wrong_format(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = '122.62.52'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_some_node_ip_components_are_negative(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = '122.-1.52.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_some_node_ip_components_are_higher_than_upper_bound(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = '122.62.256.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_ip_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_IP] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_ip_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][NODE_IP]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields - node_ip')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_is_negative(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_PORT] = -1
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'network port out of the range 0-65535')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_is_higher_than_upper_bound(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_PORT] = 65536
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'network port out of the range 0-65535')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_is_float(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_PORT] = 5555.5
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_has_wrong_format(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_PORT] = 'ninety'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][NODE_PORT] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types ')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_node_port_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][NODE_PORT]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields - node_port')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_ip_contains_leading_space(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = ' 122.62.52.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_ip_contains_trailing_space(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = '122.62.52.13 '
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_ip_has_wrong_format(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = '122.62.52'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_some_client_ip_components_are_negative(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = '122.-1.52.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_some_client_ip_components_are_higher_than_upper_bound(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = '122.62.256.13'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_ip_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_IP] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid network ip address')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_ip_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][CLIENT_IP]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields - client_ip')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_is_negative(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_PORT] = -1
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'network port out of the range 0-65535')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_is_higher_than_upper_bound(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_PORT] = 65536
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'network port out of the range 0-65535')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_is_float(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_PORT] = 5555.5
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_has_wrong_format(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_PORT] = 'ninety'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][CLIENT_PORT] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_client_port_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][CLIENT_PORT]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields - client_port')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_alias_is_empty(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][ALIAS] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'empty string')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_alias_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][ALIAS]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields ')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_services_contains_unknown_value(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][SERVICES] = [VALIDATOR, 'DECIDER']
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'unknown value')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_services_is_validator_value(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][SERVICES] = VALIDATOR  # just string, not array
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_services_is_empty_string(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][SERVICES] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'expected types')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_success_if_data_contains_unknown_field(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'][SERVICES] = []
    node_request['operation']['data']['extra'] = 42
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestRejectedException,
                         'action is not allowed')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_data_is_empty_json(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'] = {}
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields ')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_data_is_broken_json(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'] = "{'node_ip': '10.0.0.105', 'node_port': 9701"
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid type')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_fails_if_data_is_not_json(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'] = 'not_json'
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid type')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_has_invalid_syntax_if_data_is_empty_string(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['data'] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid type')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_has_invalid_syntax_if_data_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data']
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'missed fields')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.skip(reason='INDY-1864')
def test_send_node_has_invalid_syntax_if_unknown_parameter_is_passed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    node_request['operation']['albus'] = 'severus'
    steward_wallet, node = sdk_node_theta_added
    signed_reqs = sdk_sign_request_strings(looper, steward_wallet, [node_request])
    request_couple = sdk_send_signed_requests(sdk_pool_handle, signed_reqs)[0]
    sdk_get_and_check_replies(looper, [request_couple])
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_has_invalid_syntax_if_all_parameters_are_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    for f in node_request['operation'].keys():
        node_request['operation'][f] = ''
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'invalid type')
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)


@pytest.mark.node_txn
def test_send_node_succeeds_if_services_is_missed(
        looper, sdk_pool_handle, nodeSet, sdk_node_theta_added, node_request):
    del node_request['operation']['data'][SERVICES]
    steward_wallet, node = sdk_node_theta_added
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        json.dumps(node_request))
    sdk_get_and_check_replies(looper, [request_couple])
    ensurePoolIsOperable(looper, sdk_pool_handle, steward_wallet)
