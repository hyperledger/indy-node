import itertools
import pytest

from plenum.common.constants import TARGET_NYM, RAW, ENC, HASH
from indy_common.constants import TXN_TYPE, allOpKeys, ATTRIB, GET_ATTR, \
    DATA, GET_NYM, reqOpKeys, GET_TXNS, GET_SCHEMA, GET_CLAIM_DEF, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, CONFIG_LEDGER_ID, POOL_UPGRADE, POOL_CONFIG, \
    IN_PROGRESS, DISCLO, ATTR_NAMES, REVOCATION, SCHEMA, ENDPOINT, CLAIM_DEF, REF, SIGNATURE_TYPE, SCHEDULE, SHA256, \
    TIMEOUT, JUSTIFICATION, JUSTIFICATION_MAX_SIZE, REINSTALL, WRITES
from indy_common.types import ClientAttribOperation


validator = ClientAttribOperation()

VALID_TARGET_NYM = 'a' * 43


def test_attrib_with_enc_raw_hash_at_same_time_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{}',
        ENC: 'foo',
        HASH: 'bar'
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match("validation error \[ClientAttribOperation\]: only one field "
                  "from {}, {}, {} is expected"
                  "".format(RAW, ENC, HASH))


def test_attrib_without_enc_raw_hash_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: missed fields - {}, {}, {}"
        "".format(
            RAW,
            ENC,
            HASH))


def test_attrib_with_raw_string_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: 'foo',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match("validation error \[ClientAttribOperation\]: should be a "
                  "valid JSON string \({}=foo\)".format(RAW))


def test_attrib_with_raw_empty_json_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: should contain one attribute "
        "\({}={{}}\)".format(RAW))


def test_attrib_with_raw_array_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '[]',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: should be a dict "
        "\({}=<class 'list'>\)".format(RAW))


def test_attrib_with_raw_having_more_one_attrib_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"attr1": "foo", "attr2": "bar"}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: should contain one attribute "
        "\({}={{.*}}\)".format(RAW))


def test_attrib_with_raw_having_one_attrib_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"attr1": "foo"}',
    }
    validator.validate(msg)


def test_attrib_with_raw_having_endpoint_equal_null_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": null}',
    }
    validator.validate(msg)


def test_attrib_with_raw_having_endpoint_ha_equal_null_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": null}}',
    }
    validator.validate(msg)


def test_attrib_with_raw_having_endpoint_without_ha_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"foo": "bar"}}',
    }
    validator.validate(msg)


def test_attrib_with_raw_having_endpoint_ha_with_ip_address_only_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "8.8.8.8"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: invalid endpoint format ip_address:port "
        "\({}={{'ha': '8.8.8.8'}}\)".format(ENDPOINT))


def test_attrib_with_raw_having_endpoint_ha_with_invalid_port_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "8.8.8.8:65536"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: invalid endpoint port "
        "\(ha=8.8.8.8:65536\)")


def test_attrib_with_raw_having_endpoint_ha_with_invalid_ip_address_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "256.8.8.8:9700"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        "validation error \[ClientAttribOperation\]: invalid endpoint address "
        "\(ha=256.8.8.8:9700\)")
