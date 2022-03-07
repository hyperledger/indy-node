import json
from random import randint
from typing import Any, Dict, Union

from indy_common.constants import GET_NYM, NYM


def build_nym_request(
    identifier: str,
    dest: str,
    verkey: str = None,
    diddoc_content: Union[dict, str] = None,
    role: str = None
):
    request = {
        "identifier": identifier,
        "reqId": randint(100, 1000000),
        "protocolVersion": 2
    }

    operation = {
        "dest": dest,
        "type": NYM
    }

    if verkey:
        operation["verkey"] = verkey
    if diddoc_content:
        operation["diddocContent"] = (
            json.dumps(diddoc_content)
            if isinstance(diddoc_content, dict)
            else diddoc_content
        )
    if role:
        operation["role"] = role

    request["operation"] = operation
    return json.dumps(request)


def build_get_nym_request(
    identifier: str, dest: str, timestamp: int = None, seq_no: int = None
):
    request = {
        "identifier": identifier,
        "reqId": randint(100, 1000000),
        "protocolVersion": 2
    }

    operation: Dict[str, Any] = {
        "dest": dest,
        "type": GET_NYM
    }

    if timestamp:
        operation["timestamp"] = timestamp

    if seq_no:
        operation["seqNo"] = seq_no

    request["operation"] = operation
    return json.dumps(request)
