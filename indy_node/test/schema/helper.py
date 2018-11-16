from indy_common.constants import SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_FROM, GET_SCHEMA, TXN_TYPE, DATA
from indy_node.test.api.helper import validate_write_reply, sdk_write_schema, validate_schema_txn
from plenum.test.helper import sdk_sign_request_from_dict


def send_schema_and_prepare(looper, sdk_pool_handle,
                            sdk_wallet_trust_anchor, schema_name,
                            schema_version, schema_attr, other_wallet=None):
    _, issuer_id = sdk_wallet_trust_anchor

    _, rep = sdk_write_schema(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        schema_attr,
        schema_name,
        schema_version
    )

    validate_write_reply(rep)
    validate_schema_txn(rep['result']['txn'])

    op = {
        SCHEMA_FROM: issuer_id,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            SCHEMA_NAME: schema_name,
            SCHEMA_VERSION: schema_version,
        }
    }
    if other_wallet:
        return \
            sdk_sign_request_from_dict(looper, other_wallet, op)
    else:
        return \
            sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, op)
