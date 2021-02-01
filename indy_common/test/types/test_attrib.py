import json

import pytest
from libnacl.secret import SecretBox

from indy_common.constants import TXN_TYPE, ATTRIB, ENDPOINT
from indy_common.types import ClientAttribOperation
from plenum.common.constants import TARGET_NYM, RAW, ENC, HASH

validator = ClientAttribOperation()

VALID_TARGET_NYM = 'a' * 43
VALID_HASH = '6d4a333838d0ef96756cccC680AF2531075C512502Fb68c5503c63d93de859b3'
assert len(VALID_HASH) == 64


@pytest.mark.types
def test_attrib_with_enc_raw_hash_at_same_time_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{}',
        ENC: 'foo',
        HASH: VALID_HASH
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: only one field "
                  "from {}, {}, {} is expected"
                  "".format(RAW, ENC, HASH))


@pytest.mark.types
def test_attrib_without_enc_raw_hash_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: missed fields - {}, {}, {}"
        "".format(
            RAW,
            ENC,
            HASH))


@pytest.mark.types
def test_attrib_with_raw_string_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: 'foo',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: should be a "
                  r"valid JSON string \({}=foo\)".format(RAW))


@pytest.mark.types
def test_attrib_with_raw_empty_json_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: should contain one attribute "
        r"\({}={{}}\)".format(RAW))


@pytest.mark.types
def test_attrib_with_raw_array_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '[]',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: should be a dict "
        r"\({}=<class 'list'>\)".format(RAW))


@pytest.mark.types
def test_attrib_with_raw_having_more_one_attrib_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"attr1": "foo", "attr2": "bar"}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: should contain one attribute "
        r"\({}={{.*}}\)".format(RAW))


@pytest.mark.types
def test_attrib_with_raw_having_one_attrib_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"attr1": "foo"}',
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_equal_null_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": null}',
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_ha_equal_null_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": null}}',
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_without_ha_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"foo": "bar"}}',
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_ha_with_ip_address_only_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "8.8.8.8"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: invalid endpoint format ip_address:port "
        r"\({}={{'ha': '8.8.8.8'}}\)".format(ENDPOINT))


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_ha_with_invalid_port_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "8.8.8.8:65536"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: invalid endpoint port "
        r"\(ha=8.8.8.8:65536\)")


@pytest.mark.types
def test_attrib_with_raw_having_endpoint_ha_with_invalid_ip_address_fails():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        RAW: '{"endpoint": {"ha": "256.8.8.8:9700"}}',
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(
        r"validation error \[ClientAttribOperation\]: invalid endpoint address "
        r"\(ha=256.8.8.8:9700\)")


@pytest.mark.types
def test_attrib_with_valid_hash_passes():
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: VALID_HASH
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_shorter_hash_fails():
    invalid_hash = VALID_HASH[:-1]
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: invalid_hash
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: not a valid hash "
                  r"\(needs to be in hex too\) \({}={}\)".format(HASH, invalid_hash))


@pytest.mark.types
def test_attrib_with_longer_hash_fails():
    invalid_hash = VALID_HASH + 'a'
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: invalid_hash
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: not a valid hash "
                  r"\(needs to be in hex too\) \({}={}\)".format(HASH, invalid_hash))


@pytest.mark.types
def test_attrib_with_invalid_hash_fails():
    idx = 10
    invalid_hash = VALID_HASH[:idx] + 'X' + VALID_HASH[idx + 1:]
    assert len(invalid_hash) == 64
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: invalid_hash
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: not a valid hash "
                  r"\(needs to be in hex too\) \({}={}\)".format(HASH, invalid_hash))


@pytest.mark.types
def test_attrib_with_empty_hash_fails():
    empty_hash = ''
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: empty_hash
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: not a valid hash "
                  r"\(needs to be in hex too\) \({}={}\)".format(HASH, empty_hash))

    empty_hash = None
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        HASH: empty_hash
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: expected types "
                  r"'str', got 'NoneType' \({}={}\)".format(HASH, empty_hash))


@pytest.mark.types
def test_attrib_with_enc_passes():
    secretBox = SecretBox()
    enc_data = secretBox.encrypt(json.dumps({'name': 'Alice'}).encode()).hex()

    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        ENC: enc_data
    }
    validator.validate(msg)


@pytest.mark.types
def test_attrib_with_empty_enc_fails():
    empty_enc = ''
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        ENC: empty_enc
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: "
                  r"empty string \({}={}\)".format(ENC, empty_enc))

    empty_enc = None
    msg = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: VALID_TARGET_NYM,
        ENC: empty_enc
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)
    ex_info.match(r"validation error \[ClientAttribOperation\]: expected types "
                  r"'str', got 'NoneType' \({}={}\)".format(ENC, empty_enc))
