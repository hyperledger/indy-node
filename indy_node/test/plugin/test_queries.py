from indy_crypto.big_number import BigNumber

from indy_client.test.conftest import nodeSet
from indy_node.server.plugin.agent_authz.constants import ADDRESS, \
    GET_AGENT_AUTHZ, GET_AGENT_AUTHZ_ACCUM, ACCUMULATOR_ID, ACCUMULATOR_1, \
    GET_AGENT_AUTHZ_ACCUM_WIT, COMMITMENT
from indy_node.test.plugin.test_policy_creation import policy_created
from indy_node.test.plugin.test_authorize_agents import prove_grant_given, \
    prove_revoke_given
from indy_node.test.plugin.test_authorize_agents import give_prove
from plenum.common.constants import TXN_TYPE
from plenum.test.conftest import sdk_wallet_handle, \
    sdk_wallet_client, sdk_pool_handle, sdk_pool_name
from plenum.test.helper import sdk_gen_request, \
    sdk_sign_and_submit_req_obj, sdk_get_reply, sdk_eval_timeout


def get_result_data_for_op(looper, wallet_client, sdk_pool_handle, op):
    req_obj = sdk_gen_request(op, identifier=wallet_client[1])
    req = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle,
                                      wallet_client, req_obj)
    _, resp_task = sdk_get_reply(looper, req, timeout=sdk_eval_timeout(1, 4))
    return resp_task['result']['data']


def test_get_accumulator(looper, nodeSet, agent1_wallet, agent1_client,
                         policy_created, query_wallet_client, sdk_pool_handle):
    """
    Add new agents with commitments and check that accumulator gets updated by
    using `GET_AGENT_AUTHZ_ACCUM`.
    Revoke `PROVE`authorisation of existing agents
    Use `GET_AGENT_AUTHZ_ACCUM` to check that accumulator gets changes after
    each of the above
    """
    config = nodeSet[0].config
    op = {
        TXN_TYPE: GET_AGENT_AUTHZ_ACCUM,
        ACCUMULATOR_ID: ACCUMULATOR_1
    }

    addr, admin_verkey, admin_auth, admin_commitment = policy_created
    v1 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)

    _, _, _, commitment1 = give_prove(looper, addr, admin_verkey,
                                      agent1_wallet, agent1_client)
    v2 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert BigNumber.modular_exponentiation(int(v1), commitment1,
                                            config.AuthzAccumMod[ACCUMULATOR_1]) == int(v2)

    _, _, _, commitment2 = give_prove(looper, addr, admin_verkey,
                                      agent1_wallet, agent1_client)
    v3 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert BigNumber.modular_exponentiation(int(v2), commitment2,
                                            config.AuthzAccumMod[ACCUMULATOR_1]) == int(v3)

    _, _, _, commitment3 = give_prove(looper, addr, admin_verkey,
                                      agent1_wallet, agent1_client)
    v4 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert BigNumber.modular_exponentiation(int(v3), commitment3,
                                            config.AuthzAccumMod[ACCUMULATOR_1]) == int(v4)

    # Witness
    # _, _, _, commitment4 = give_prove(looper, addr, admin_verkey,
    #                                   agent1_wallet, agent1_client)
    # _, _, _, commitment5 = give_prove(looper, addr, admin_verkey,
    #                                   agent1_wallet, agent1_client)
    op = {
        TXN_TYPE: GET_AGENT_AUTHZ_ACCUM_WIT,
        ACCUMULATOR_ID: ACCUMULATOR_1,
        COMMITMENT: commitment1
    }
    v5 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert v5[0] == v4  # Latest accumulator
    assert v5[1] == v1  # Accumulator before adding commitment1
    assert v5[2] == [str(commitment2), str(commitment3)]  # Commitments added after adding commitment1

    op = {
        TXN_TYPE: GET_AGENT_AUTHZ_ACCUM_WIT,
        ACCUMULATOR_ID: ACCUMULATOR_1,
        COMMITMENT: admin_commitment
    }
    v6 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert v6[0] == v4  # Latest accumulator
    assert v6[2] == [str(commitment1), str(commitment2), str(commitment3)] # Commitments added after adding admin_commitment

    op = {
        TXN_TYPE: GET_AGENT_AUTHZ_ACCUM_WIT,
        ACCUMULATOR_ID: ACCUMULATOR_1,
        COMMITMENT: commitment2
    }
    v7 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert v7[0] == v4  # Latest accumulator
    assert v7[1] == v2  # Accumulator before adding commitment2
    assert v7[2] == [str(commitment3)]  # Commitments added after adding commitment2

    op = {
        TXN_TYPE: GET_AGENT_AUTHZ_ACCUM_WIT,
        ACCUMULATOR_ID: ACCUMULATOR_1,
        COMMITMENT: commitment3
    }
    v8 = get_result_data_for_op(looper, query_wallet_client, sdk_pool_handle,
                                op)
    assert v8[0] == v4  # Latest accumulator
    assert v8[1] == v3  # Accumulator before adding commitment3
    assert v8[2] == []  # Commitments added after adding commitment3


def test_get_auth_policy_by_address(looper, nodeSet, agent1_wallet,
                                    agent1_client, policy_created,
                                    prove_grant_given, prove_revoke_given,
                                    query_wallet_client, sdk_pool_handle):
    """
    Create a new auth policy and get it from the ledger using `GET_AGENT_AUTHZ`.
    Update the policy by adding new keys.
    Update the policy by updating authorisation of existing keys.
    Use `GET_AGENT_AUTHZ` to check that above changes are successful
    """
    addr, admin_verkey, admin_auth, admin_commitment = policy_created
    _, granter_verkey, granter_auth = prove_grant_given
    _, revoker_verkey, revoker_auth = prove_revoke_given
    _, prover_verkey, prover_auth, prover_commitment = give_prove(looper, addr,
                                                                  admin_verkey,
                                                                  agent1_wallet,
                                                                  agent1_client)

    op = {
        TXN_TYPE: GET_AGENT_AUTHZ,
        ADDRESS: addr
    }
    data = get_result_data_for_op(looper, query_wallet_client,
                                  sdk_pool_handle, op)

    assert [admin_verkey, admin_auth, str(admin_commitment)] in data
    assert [granter_verkey, granter_auth, '0'] in data
    assert [revoker_verkey, revoker_auth, '0'] in data
    assert [prover_verkey, prover_auth, str(prover_commitment)] in data
