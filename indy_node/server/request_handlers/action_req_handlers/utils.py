from plenum.common.request import Request
from plenum.common.types import f


def generate_action_result(request: Request):
    return {**request.operation, **{
        f.IDENTIFIER.nm: request.identifier,
        f.REQ_ID.nm: request.reqId}}
