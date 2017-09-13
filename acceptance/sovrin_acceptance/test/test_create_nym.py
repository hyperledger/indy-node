import pytest


@pytest.mark.asyncio
async def test_create_nym(client):
    my_did, my_verkey = await client.new_did()

    await client.new_did(seed='000000000000000000000000Trustee1')
    await client.send_nym(dest=my_did, verkey=my_verkey)
    gotten_nym = await client.send_get_nym(dest=my_did)

    assert gotten_nym['dest'] == my_did
    assert gotten_nym['verkey'] == my_verkey
