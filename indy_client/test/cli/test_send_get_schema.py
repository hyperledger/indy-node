import json
import pytest

from indy_node.test.schema.helper import write_schema, prepare_get_schema_and_send
from indy.ledger import parse_get_schema_response


def test_send_get_schema_succeeds(looper, sdk_pool_handle,
                                  sdk_wallet_trust_anchor):
    _, issuer_id = sdk_wallet_trust_anchor

    schema_name = "Faber"
    schema_version = "1.8"
    schema_attr = ["attribute1"]

    write_schema(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        schema_name, schema_version,
        schema_attr)

    rep = prepare_get_schema_and_send(looper, issuer_id, sdk_pool_handle,
                                      sdk_wallet_trust_anchor, schema_name,
                                      schema_version)
    print(rep)
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(rep[0])))


def test_send_get_schema_as_alice(looper, sdk_pool_handle,
                                  sdk_wallet_trust_anchor, sdk_wallet_client):
    _, issuer_id = sdk_wallet_trust_anchor

    schema_name = "Saber"
    schema_version = "1.3"
    schema_attr = ["attribute1", "attribute2"]

    write_schema(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        schema_name, schema_version,
        schema_attr)

    prepare_get_schema_and_send(looper, issuer_id, sdk_pool_handle,
                                sdk_wallet_trust_anchor, schema_name,
                                schema_version, sdk_wallet_client)


def test_send_get_schema_fails_with_invalid_name(looper, sdk_pool_handle,
                                                 sdk_wallet_trust_anchor):
    _, issuer_id = sdk_wallet_trust_anchor

    schema_name = "Business_1"
    schema_version = "1.8"
    schema_attr = ["attribute1"]

    write_schema(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        schema_name, schema_version,
        schema_attr)

    prepare_get_schema_and_send(looper, issuer_id,
                                sdk_wallet_trust_anchor, "not_Business_1",
                                schema_version)

#
# def test_send_get_schema_fails_with_invalid_dest(looper, sdk_pool_handle,
#                                                  sdk_wallet_trust_anchor):
#     uuid_identifier = createUuidIdentifier()
#     do('send GET_SCHEMA dest={} name=invalid version=1.0'.format(
#         uuid_identifier), expect=SCHEMA_NOT_FOUND, within=5)
#
#
# def test_send_get_schema_fails_with_invalid_version(
#         be, do, poolNodesStarted, trusteeCli, send_schema):
#     do('send GET_SCHEMA dest={} name=Degree version=2.0'.format(
#         trusteeCli.activeDID), expect=SCHEMA_NOT_FOUND, within=5)
#
#
# def test_send_get_schema_fails_with_invalid_version_syntax(
#         be, do, poolNodesStarted, trusteeCli, send_schema):
#     with pytest.raises(AssertionError) as excinfo:
#         do('send GET_SCHEMA dest={} name=Degree version=asdf'.format(
#             trusteeCli.activeDID), expect=SCHEMA_NOT_FOUND, within=5)
#     assert (INVALID_SYNTAX in str(excinfo.value))
#
#
# def test_send_get_schema_fails_without_version(
#         be, do, poolNodesStarted, trusteeCli, send_schema):
#     with pytest.raises(AssertionError) as excinfo:
#         do('send GET_SCHEMA dest={} name=Degree'.format(trusteeCli.activeDID),
#            expect=SCHEMA_NOT_FOUND, within=5)
#     assert (INVALID_SYNTAX in str(excinfo.value))
#
#
# def test_send_get_schema_fails_without_name(
#         be, do, poolNodesStarted, trusteeCli, send_schema):
#     with pytest.raises(AssertionError) as excinfo:
#         do('send GET_SCHEMA dest={} version=1.0'.format(trusteeCli.activeDID),
#            expect=SCHEMA_NOT_FOUND, within=5)
#     assert (INVALID_SYNTAX in str(excinfo.value))
#
#
# def test_send_get_schema_fails_without_dest(
#         be, do, poolNodesStarted, trusteeCli, send_schema):
#     with pytest.raises(AssertionError) as excinfo:
#         do('send GET_SCHEMA name=Degree version=1.0',
#            expect=SCHEMA_NOT_FOUND, within=5)
#     assert (INVALID_SYNTAX in str(excinfo.value))
