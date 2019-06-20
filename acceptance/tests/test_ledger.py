from utils import pool_helper, wallet_helper, nym_helper, get_nym_helper, attrib_helper, get_attrib_helper,\
    schema_helper, get_schema_helper, cred_def_helper, get_cred_def_helper, revoc_reg_def_helper,\
    get_revoc_reg_def_helper, revoc_reg_entry_helper, get_revoc_reg_helper, get_revoc_reg_delta_helper,\
    random_did_and_json, random_seed_and_json
import pytest
import json
from indy import pool, did, ledger, IndyError
import hashlib
import time


@pytest.mark.parametrize('writer_role', ['TRUSTEE', 'STEWARD', 'ENDORSER'])
@pytest.mark.parametrize('reader_role', ['TRUSTEE', 'STEWARD', 'ENDORSER', None])
@pytest.mark.asyncio
async def test_send_and_get_nym_positive(writer_role, reader_role):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    writer_did, writer_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    reader_did, reader_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds NYM writer
    await nym_helper(pool_handle, wallet_handle, trustee_did, writer_did, writer_vk, None, writer_role)
    # Trustee adds NYM reader
    await nym_helper(pool_handle, wallet_handle, trustee_did, reader_did, reader_vk, None, reader_role)
    # Writer sends NYM
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, writer_did, target_did))
    time.sleep(1)
    # Reader gets NYM
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, target_did, target_did))

    assert res1['op'] == 'REPLY'
    assert res2['result']['seqNo'] is not None

    print(res1)
    print(res2)


@pytest.mark.parametrize('submitter_seed', ['{}',
                                            random_did_and_json()[1],
                                            random_seed_and_json()[1],
                                            ])
@pytest.mark.asyncio
async def test_send_and_get_nym_negative(submitter_seed):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, submitter_seed)
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds submitter
    await nym_helper(pool_handle, wallet_handle, trustee_did, submitter_did, submitter_vk)
    # None role submitter tries to send NYM (rejected) and gets no data about this NYM from ledger
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, submitter_did, target_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, submitter_did, target_did))

    assert res1['op'] == 'REJECT'
    assert res2['result']['seqNo'] is None

    print(res1)
    print(res2)


@pytest.mark.parametrize('xhash, raw, enc', [
    (hashlib.sha256().hexdigest(), None, None),
    (None, json.dumps({'key': 'value'}), None),
    (None, None, 'ENCRYPTED_STRING')
])
@pytest.mark.asyncio
async def test_send_and_get_attrib_positive(xhash, raw, enc):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk)
    res1 = json.loads(await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
    res2 = json.loads(await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))

    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'

    print(res1)
    print(res2)


@pytest.mark.parametrize('xhash, raw, enc, error', [
    (None, None, None, IndyError),
    (hashlib.sha256().hexdigest(), json.dumps({'key': 'value'}), None, None),
    (None, json.dumps({'key': 'value'}), 'ENCRYPTED_STRING', None),
    (hashlib.sha256().hexdigest(), None, 'ENCRYPTED_STRING', None),
    (hashlib.sha256().hexdigest(), json.dumps({'key': 'value'}), 'ENCRYPTED_STRING', None)
])
@pytest.mark.asyncio
async def test_send_and_get_attrib_negative(xhash, raw, enc, error):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk)
    if error:
        with pytest.raises(error):
            await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc)
            await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc)
    else:
        res1 = json.loads(await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
        res2 = json.loads(await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))

        assert res1['op'] == 'REQNACK'
        assert res2['op'] == 'REQNACK'

        print(res1)
        print(res2)


@pytest.mark.parametrize('writer_role', ['TRUSTEE', 'STEWARD', 'ENDORSER'])
@pytest.mark.parametrize('reader_role', ['TRUSTEE', 'STEWARD', 'ENDORSER', None])
@pytest.mark.asyncio
async def test_send_and_get_schema_positive(writer_role, reader_role):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    writer_did, writer_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    reader_did, reader_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds SCHEMA writer
    await nym_helper(pool_handle, wallet_handle, trustee_did, writer_did, writer_vk, None, writer_role)
    # Trustee adds SCHEMA reader
    await nym_helper(pool_handle, wallet_handle, trustee_did, reader_did, reader_vk, None, reader_role)
    # Writer sends SCHEMA
    schema_id, res = await schema_helper(pool_handle, wallet_handle, writer_did,
                                         'schema1', '1.0', json.dumps(["age", "sex", "height", "name"]))
    res1 = json.loads(res)
    # Reader gets SCHEMA
    res2 = json.loads(await get_schema_helper(pool_handle, wallet_handle, reader_did, schema_id))

    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'

    print(res1)
    print(res2)


@pytest.mark.skip('IS-932')
@pytest.mark.asyncio
async def test_send_and_get_schema_negative():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    res = await get_schema_helper(pool_handle, wallet_handle, trustee_did,
                                  '7kqbG8zcdAMc9Q6SMU4xZy:2:schema1:1.0')
    res_json = json.loads(res)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)

    assert res_json
    print(schema_id, schema_json)


@pytest.mark.parametrize('writer_role', ['TRUSTEE', 'STEWARD', 'ENDORSER'])
@pytest.mark.parametrize('reader_role', ['TRUSTEE', 'STEWARD', 'ENDORSER', None])
@pytest.mark.asyncio
async def test_send_and_get_cred_def_positive(writer_role, reader_role):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    writer_did, writer_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    reader_did, reader_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds CRED_DEF writer
    await nym_helper(pool_handle, wallet_handle, trustee_did, writer_did, writer_vk, None, writer_role)
    # Trustee adds CRED_DEF reader
    await nym_helper(pool_handle, wallet_handle, trustee_did, reader_did, reader_vk, None, reader_role)
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, writer_did,
                                       'schema1', '1.0', json.dumps(["age", "sex", "height", "name"]))
    time.sleep(1)
    res = await get_schema_helper(pool_handle, wallet_handle, reader_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, writer_did, schema_json, 'TAG',
                                                None, json.dumps({'support_revocation': False}))
    res1 = json.loads(res)
    res2 = json.loads(await get_cred_def_helper(pool_handle, wallet_handle, reader_did, cred_def_id))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)
    print(cred_def_id)


@pytest.mark.skip('IS-932')
@pytest.mark.asyncio
async def test_send_and_get_cred_def_negative():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    res = await get_cred_def_helper(pool_handle, wallet_handle, trustee_did,
                                    'AfdMw5jMX9pcNAuSwppbC7:3:CL:297:cred_def_tag')
    res_json = json.loads(res)
    cred_def_id, cred_def_json = await ledger.parse_get_cred_def_response(res)

    assert res_json
    print(cred_def_id, cred_def_json)


@pytest.mark.parametrize('writer_role', ['TRUSTEE', 'STEWARD', 'ENDORSER'])
@pytest.mark.parametrize('reader_role', ['TRUSTEE', 'STEWARD', 'ENDORSER', None])
@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_def_positive(writer_role, reader_role):
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    writer_did, writer_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    reader_did, reader_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds REVOC_REG_DEF writer
    await nym_helper(pool_handle, wallet_handle, trustee_did, writer_did, writer_vk, None, writer_role)
    # Trustee adds REVOC_REG_DEF reader
    await nym_helper(pool_handle, wallet_handle, trustee_did, reader_did, reader_vk, None, reader_role)
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, writer_did,
                                       'schema1', '1.0', json.dumps(["age", "sex", "height", "name"]))
    time.sleep(1)
    res = await get_schema_helper(pool_handle, wallet_handle, reader_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, writer_did, schema_json, 'cred_def_tag',
                                                None, json.dumps({"support_revocation": True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_def_helper(pool_handle, wallet_handle, writer_did, None,
                                                              'revoc_def_tag', cred_def_id,
                                                              json.dumps({'max_cred_num': 1,
                                                                          'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    res2 = await get_revoc_reg_def_helper(pool_handle, wallet_handle, reader_did, revoc_reg_def_id)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_def_negative():
    pass


@pytest.mark.parametrize('writer_role', ['TRUSTEE', 'STEWARD', 'ENDORSER'])
@pytest.mark.parametrize('reader_role', ['TRUSTEE', 'STEWARD', 'ENDORSER', None])
@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_entry_positive(writer_role, reader_role):
    await pool.set_protocol_version(2)
    timestamp0 = int(time.time())
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    writer_did, writer_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    reader_did, reader_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    # Trustee adds REVOC_REG_ENTRY writer
    await nym_helper(pool_handle, wallet_handle, trustee_did, writer_did, writer_vk, None, writer_role)
    # Trustee adds REVOC_REG_ENTRY reader
    await nym_helper(pool_handle, wallet_handle, trustee_did, reader_did, reader_vk, None, reader_role)
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, writer_did,
                                       'schema1', '1.0', json.dumps(["age", "sex", "height", "name"]))
    time.sleep(1)
    res = await get_schema_helper(pool_handle, wallet_handle, reader_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, writer_did, schema_json, 'cred_def_tag',
                                                'CL', json.dumps({'support_revocation': True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_entry_helper(pool_handle, wallet_handle, writer_did, 'CL_ACCUM',
                                                                'revoc_def_tag', cred_def_id,
                                                                json.dumps({'max_cred_num': 1,
                                                                            'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    timestamp1 = int(time.time())
    res2 = await get_revoc_reg_helper(pool_handle, wallet_handle, reader_did, revoc_reg_def_id, timestamp1)
    res3 = await get_revoc_reg_delta_helper(pool_handle, wallet_handle, reader_did, revoc_reg_def_id,
                                            timestamp0, timestamp1)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    assert res3['op'] == 'REPLY'
    print(res1)
    print(res2)
    print(res3)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_entry_negative():
    pass
