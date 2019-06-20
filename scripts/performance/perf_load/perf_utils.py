import json
import os
import argparse
from collections import Sequence
from typing import Dict, List

import base58
import libnacl
import logging
import time

PUB_XFER_TXN_ID = "10001"

logger = logging.getLogger()


def logger_init(out_dir, f_name, log_lvl):
    od = os.path.expanduser(out_dir)
    os.makedirs(od, exist_ok=True)
    logging.basicConfig(filename=os.path.join(od, f_name), level=log_lvl, style="{",
                        format='{asctime:s}|{levelname:s}|{filename:s}|{name:s}|{message:s}')
    logging.Formatter.converter = time.gmtime


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


def request_get_type(req):
    if isinstance(req, dict):
        dict_req = req
    elif isinstance(req, str):
        dict_req = json.loads(req)
    else:
        raise RuntimeError("Request of unsupported type")
    txn_type = dict_req.get("operation", {}).get("type", "")
    return txn_type


def response_get_type(req):
    if isinstance(req, dict):
        dict_resp = req
    elif isinstance(req, str):
        dict_resp = json.loads(req)
    else:
        raise RuntimeError("Response of unsupported type")
    txn_type = dict_resp.get("result", {}).get("txn", {}).get("type", "")
    return txn_type


def log_addr_txos_update(context: str, addr_txos: Dict[str, List], amount: int = 0):
    total = sum(len(txos) for txos in addr_txos.values())
    if amount > 0:
        logger.info("{}: added {} txos, {} total in addr_txos".format(context, amount, total))
    elif amount < 0:
        logger.info("{}: removed {} txos, {} total in addr_txos".format(context, -amount, total))
    else:
        logger.info("{}: {} txos total in addr_txos".format(context, total))


def gen_input_output(addr_txos, val):
    for address in addr_txos:
        inputs = []
        outputs = []
        total_amount = 0
        tmp_txo = []
        while addr_txos[address] and total_amount < val:
            (source, amount) = addr_txos[address].pop()
            if amount > 0:
                inputs.append(source)
                total_amount += amount
                tmp_txo.append((source, amount))

        if total_amount >= val:
            out_val = total_amount - val
            if out_val > 0:
                outputs = [{"recipient": address, "amount": out_val}]
            return {address: tmp_txo}, inputs, outputs
        else:
            for s_a in tmp_txo:
                addr_txos[address].append(s_a)

    return None, None, None
