import json

import pytest
from indy import ledger, signus


@pytest.mark.asyncio
async def test_create_nym_old(pool_handle, wallet_handle):
    trustee_did_params = json.dumps(
        {'seed': '000000000000000000000000Trustee1'})

    trustee_did, _, _ = \
        await signus.create_and_store_my_did(wallet_handle, trustee_did_params)

    my_did, my_verkey, _ = \
        await signus.create_and_store_my_did(wallet_handle, json.dumps({}))

    nym_req_json = \
        await ledger.build_nym_request(trustee_did, my_did, my_verkey,
                                       None, None)

    signed_nym_req_json = \
        await ledger.sign_request(wallet_handle, trustee_did, nym_req_json)

    await ledger.submit_request(pool_handle, signed_nym_req_json)

    get_nym_req_json = await ledger.build_get_nym_request(trustee_did, my_did)

    get_nym_resp_json = \
        await ledger.submit_request(pool_handle, get_nym_req_json)

    get_nym_resp = json.loads(get_nym_resp_json)
    get_nym_res_data = json.loads(get_nym_resp['result']['data'])

    assert get_nym_res_data['dest'] == my_did
    assert get_nym_res_data['verkey'] == my_verkey
