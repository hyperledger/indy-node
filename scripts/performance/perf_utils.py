import json
import os
import argparse
from collections import Sequence
import base58
import libnacl


def check_fs(is_dir: bool, fs_name: str):
    pp = os.path.expanduser(fs_name)
    rights = os.W_OK if is_dir else os.R_OK
    chk_func = os.path.isdir if is_dir else os.path.isfile
    size_check = True if is_dir else os.path.getsize(pp) > 0
    if chk_func(pp) and os.access(pp, rights) and size_check:
        return pp
    raise argparse.ArgumentTypeError("{} not found or access error or file empty".format(pp))


def check_seed(seed: str):
    if len(seed) == 32:
        return seed
    raise argparse.ArgumentTypeError("Seed must be 32 characters long but provided {}".format(len(seed)))


def ensure_is_reply(resp):
    if isinstance(resp, str):
        resp = json.loads(resp)
    if "op" not in resp or resp["op"] != "REPLY":
        raise Exception("Response is not a successful reply: {}".format(resp))


def divide_sequence_into_chunks(seq: Sequence, chunk_size: int):
    return (seq[shift:shift + chunk_size] for shift in range(0, len(seq), chunk_size))


# Copied from Plenum
def rawToFriendly(raw):
    return base58.b58encode(raw).decode("utf-8")


# Copied from Plenum
def random_string(sz: int) -> str:
    assert (sz > 0), "Expected random string size cannot be less than 1"
    rv = libnacl.randombytes(sz // 2).hex()
    return rv if sz % 2 == 0 else rv + hex(libnacl.randombytes_uniform(15))[-1]


def get_txn_field(txn_dict):
    tmp = txn_dict or {}
    return tmp.get('result', {}).get('txn', {}) or tmp.get('txn', {})

def get_type_field(txn_dict):
        return get_txn_field(txn_dict).get('type', None)

def get_txnid_field(txn_dict):
    tmp = txn_dict or {}
    return (tmp.get('result', {}).get('txnMetadata', {}) or tmp.get('txnMetadata', {})).get('txnId', None)
