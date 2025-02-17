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
import testinfra
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