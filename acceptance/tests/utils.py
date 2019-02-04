import json
import string
import random
import base58
from indy import pool, wallet, ledger, anoncreds, blob_storage
from ctypes import CDLL


def run_async_method(method, *args, **kwargs):

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(method(*args, **kwargs))


def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def random_did_and_json():
    return base58.b58encode(random_string(16)).decode(),\
        json.dumps({'did': base58.b58encode(random_string(16)).decode()})


def random_seed_and_json():
    return base58.b58encode(random_string(23)).decode(),\
        json.dumps({'seed': base58.b58encode(random_string(23)).decode()})


async def pool_helper(pool_name=None, path_to_genesis='./docker_genesis'):
    if not pool_name:
        pool_name = random_string(5)
    pool_config = json.dumps({"genesis_txn": path_to_genesis})
    await pool.create_pool_ledger_config(pool_name, pool_config)
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)

    return pool_handle, pool_name


async def wallet_helper(wallet_id=None, wallet_key='', wallet_key_derivation_method='ARGON2I_INT'):
    if not wallet_id:
        wallet_id = random_string(5)
    wallet_config = json.dumps({"id": wallet_id})
    wallet_credentials = json.dumps({"key": wallet_key, "key_derivation_method": wallet_key_derivation_method})
    await wallet.create_wallet(wallet_config, wallet_credentials)
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)

    return wallet_handle, wallet_config, wallet_credentials


async def pool_destructor(pool_handle, pool_name):
    await pool.close_pool_ledger(pool_handle)
    await pool.delete_pool_ledger_config(pool_name)


async def wallet_destructor(wallet_handle, wallet_config, wallet_credentials):
    await wallet.close_wallet(wallet_handle)
    await wallet.delete_wallet(wallet_config, wallet_credentials)


async def payment_initializer(library_name, initializer_name):
    library = CDLL(library_name)
    init = getattr(library, initializer_name)
    init()


async def nym_helper(pool_handle, wallet_handle, submitter_did, target_did,
                     target_vk=None, target_alias=None, target_role=None):
    req = await ledger.build_nym_request(submitter_did, target_did, target_vk, target_alias, target_role)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def attrib_helper(pool_handle, wallet_handle, submitter_did, target_did, xhash=None, raw=None, enc=None):
    req = await ledger.build_attrib_request(submitter_did, target_did, xhash, raw, enc)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def schema_helper(pool_handle, wallet_handle, submitter_did, schema_name, schema_version, schema_attrs):
    schema_id, schema_json = await anoncreds.issuer_create_schema(submitter_did, schema_name, schema_version,
                                                                  schema_attrs)
    req = await ledger.build_schema_request(submitter_did, schema_json)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return schema_id, res


async def cred_def_helper(pool_handle, wallet_handle, submitter_did, schema_json, tag, signature_type, config_json):
    cred_def_id, cred_def_json = \
        await anoncreds.issuer_create_and_store_credential_def(wallet_handle, submitter_did, schema_json, tag,
                                                               signature_type, config_json)
    req = await ledger.build_cred_def_request(submitter_did, cred_def_json)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return cred_def_id, cred_def_json, res


async def revoc_reg_def_helper(pool_handle, wallet_handle, submitter_did, revoc_def_type, tag, cred_def_id, config_json):
    tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
    tails_writer_handle = await blob_storage.open_writer('default', tails_writer_config)
    revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json = \
        await anoncreds.issuer_create_and_store_revoc_reg(wallet_handle, submitter_did, revoc_def_type, tag,
                                                          cred_def_id, config_json, tails_writer_handle)
    req = await ledger.build_revoc_reg_def_request(submitter_did, revoc_reg_def_json)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req))

    return revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json, res


async def revoc_reg_entry_helper(pool_handle, wallet_handle, submitter_did, revoc_def_type, tag, cred_def_id, config_json):
    tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
    tails_writer_handle = await blob_storage.open_writer('default', tails_writer_config)
    revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json = \
        await anoncreds.issuer_create_and_store_revoc_reg(wallet_handle, submitter_did, revoc_def_type, tag,
                                                          cred_def_id, config_json, tails_writer_handle)
    req = await ledger.build_revoc_reg_def_request(submitter_did, revoc_reg_def_json)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    req = await ledger.build_revoc_reg_entry_request(submitter_did, revoc_reg_def_id, revoc_def_type,
                                                     revoc_reg_entry_json)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req))

    return revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json, res


async def get_nym_helper(pool_handle, wallet_handle, submitter_did, target_did):
    req = await ledger.build_get_nym_request(submitter_did, target_did)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def get_attrib_helper(pool_handle, wallet_handle, submitter_did, target_did, xhash=None, raw=None, enc=None):
    req = await ledger.build_get_attrib_request(submitter_did, target_did, raw, xhash, enc)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def get_schema_helper(pool_handle, wallet_handle, submitter_did, id_):
    req = await ledger.build_get_schema_request(submitter_did, id_)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def get_cred_def_helper(pool_handle, wallet_handle, submitter_did, id_):
    req = await ledger.build_get_cred_def_request(submitter_did, id_)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)

    return res


async def get_revoc_reg_def_helper(pool_handle, wallet_handle, submitter_did, id_):
    req = await ledger.build_get_revoc_reg_def_request(submitter_did, id_)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req))

    return res


async def get_revoc_reg_helper(pool_handle, wallet_handle, submitter_did, id_, timestamp):
    req = await ledger.build_get_revoc_reg_request(submitter_did, id_, timestamp)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req))

    return res


async def get_revoc_reg_delta_helper(pool_handle, wallet_handle, submitter_did, id_, from_, to_):
    req = await ledger.build_get_revoc_reg_delta_request(submitter_did, id_, from_, to_)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req))

    return res
