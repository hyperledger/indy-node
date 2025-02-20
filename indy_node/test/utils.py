import time
from datetime import datetime, timedelta, timezone
import os
import string
from typing import Optional
import subprocess
import base58
import asyncio
from random import sample, shuffle, randrange
from collections import Counter
from collections.abc import Iterable
from inspect import isawaitable
import random
import itertools
import functools
import json
from json import JSONDecodeError
import hashlib
import indy_vdr
from indy_vdr import ledger, open_pool
from aries_askar import Store, Key, KeyAlg, AskarError, AskarErrorCode
from indy_credx import Schema, CredentialDefinition, RevocationRegistryDefinition
from indy_vdr.error import VdrError

import logging

logger = logging.getLogger(__name__)


async def create_and_store_cred_def(wallet_handle, submitter_did, schema, tag, signature_type, support_revocation):
    (
        cred_def,
        cred_def_private,
        key_proof,
    ) = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: CredentialDefinition.create(
            submitter_did,
            schema,
            signature_type or "CL",
            tag or "default",
            support_revocation=support_revocation,
        ),
    )
    cred_def_id = cred_def.id
    cred_def_json = cred_def.to_json()

    await wallet_handle.insert("credential_def", cred_def_id, cred_def_json, tags={"schema_id": schema["id"]})
    await wallet_handle.insert("credential_def_private", cred_def_id, cred_def_private.to_json_buffer())
    await wallet_handle.insert("credential_def_key_proof", cred_def_id, key_proof.to_json_buffer())
    return cred_def_id, cred_def_json

async def create_and_store_revoc_reg(wallet_handle, submitter_did, revoc_def_type, tag, cred_def_id, max_cred_num=1,
                                     issuance_type=None):
    cred_def = await wallet_handle.fetch("credential_def", cred_def_id)
    (
        rev_reg_def,
        rev_reg_def_private,
        rev_reg,
        _rev_reg_delta,
    ) = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: RevocationRegistryDefinition.create(
            submitter_did,
            cred_def.raw_value,
            tag,
            revoc_def_type,
            max_cred_num,
            issuance_type=issuance_type
        ),
    )

    rev_reg_def_id = rev_reg_def.id
    rev_reg_def_json = rev_reg_def.to_json()
    rev_reg_json = rev_reg.to_json()

    await wallet_handle.insert("revocation_reg", rev_reg_def_id, rev_reg_json)
    await wallet_handle.insert("revocation_reg_info", rev_reg_def_id, value_json={"curr_id": 0, "used_ids": []})
    await wallet_handle.insert("revocation_reg_def", rev_reg_def_id, rev_reg_def_json)
    await wallet_handle.insert("revocation_reg_def_private", rev_reg_def_id, rev_reg_def_private.to_json_buffer())
    return rev_reg_def_id, rev_reg_def_json, rev_reg_json

async def create_schema(wallet_handle, submitter_did, schema_name, schema_version, schema_attrs):
    schema = Schema.create(submitter_did, schema_name, schema_version, schema_attrs)
    schema_id = schema.id
    schema_json = schema.to_json()
    await wallet_handle.insert("schema", schema_id, schema_json)
    return schema_id, schema_json

async def get_did_signing_key(wallet_handle, did):
    item = await wallet_handle.fetch("did", did, for_update=False)
    if item:
        kp = await wallet_handle.fetch_key(item.value_json.get("verkey"))
        return kp.key
    return None

async def sign_request(wallet_handle, submitter_did, req):
    key = await get_did_signing_key(wallet_handle, submitter_did)
    if not key:
        raise Exception(f"Key for DID {submitter_did} is empty")
    req.set_signature(key.sign_message(req.signature_input))
    return req



def parse_get_schema_response(response):
    schema_seqno = response.get("seqNo")
    schema_name = response["data"]["name"]
    schema_version = response["data"]["version"]
    schema_id = f"{response['dest']}:2:{schema_name}:{schema_version}"
    return schema_id, {
        "ver": "1.0",
        "id": schema_id,
        "name": schema_name,
        "version": schema_version,
        "attrNames": response["data"]["attr_names"],
        "seqNo": schema_seqno,
    }
    
async def create_and_store_did(wallet_handle, seed=None):
    keypair, did, verkey = key_helper(seed=seed)
    await key_insert_helper(wallet_handle, keypair, did, verkey)
    return did, verkey

def key_helper(seed=None):
    alg = KeyAlg.ED25519
    if seed:
        keypair = Key.from_secret_bytes(alg, seed)
    else:
        keypair = Key.generate(alg)
    verkey_bytes = keypair.get_public_bytes()
    verkey = base58.b58encode(verkey_bytes).decode("ascii")
    did = base58.b58encode(verkey_bytes[:16]).decode("ascii")
    return keypair, did, verkey

async def key_insert_helper(wallet_handle, keypair, did, verkey):
    try:
        await wallet_handle.insert_key(verkey, keypair, metadata=json.dumps({}))
    except AskarError as err:
        if err.code == AskarErrorCode.DUPLICATE:
            pass
        else:
            raise err
    item = await wallet_handle.fetch("did", did, for_update=True)
    if item:
        did_info = item.value_json
        if did_info.get("verkey") != verkey:
            raise Exception("DID already present in wallet")
        did_info["metadata"] = {}
        await wallet_handle.replace("did", did, value_json=did_info, tags=item.tags)
    else:
        await wallet_handle.insert("did", did,
                                   value_json={
                                       "did": did,
                                       "method": "sov",
                                       "verkey": verkey,
                                       "verkey_type": "ed25519",
                                       "metadata": {},
                                   },
                                   tags={
                                       "method": "sov",
                                       "verkey": verkey,
                                       "verkey_type": "ed25519",
                                   },
        )

async def submit_request(pool_handle, req):
    request_result = await pool_handle.sumbit_request(req)
    return request_result