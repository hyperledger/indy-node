from random import randint

import pytest
from anoncreds.protocol.exceptions import SchemaNotFoundError
from anoncreds.protocol.types import ID, Schema

from plenum.common.exceptions import OperationError
from plenum.common.util import randomString
from stp_core.common.log import getlogger

logger = getlogger()
whitelist = ['Consensus for ReqId:']


def test_submit_schema(submitted_schema, schema):
    assert submitted_schema
    assert submitted_schema.seqId

    # initial schema has stub seqno - excluding seqno from comparison
    def withNoSeqId(schema):
        return schema._replace(seqId=None)

    assert withNoSeqId(submitted_schema) == withNoSeqId(schema)


def test_submit_same_schema_twice(looper, public_repo,
                                  schema,
                                  submitted_schema):
    assert submitted_schema
    with pytest.raises(OperationError) as ex_info:
        looper.run(
            public_repo.submitSchema(schema)
        )
        ex_info.match("can have one and only one SCHEMA with name GVT and version 1.0'")    # This line is unreachable in case of an exception


def test_can_not_submit_schema_by_identity_owner(looper,
                                                 public_repo_for_client,
                                                 schema):
    with pytest.raises(OperationError) as ex_info:
        looper.run(
            public_repo_for_client.submitSchema(schema)
        )
        ex_info.match("role cannot add claim def")  # This line is unreachable in case of an exception


def test_can_not_submit_schema_with_empty_attr_names(looper,
                                                     public_repo,
                                                     stewardWallet):
    schema = Schema(name='newSchema',
                    version='4.0',
                    attrNames=[],
                    issuerId=stewardWallet.defaultId,
                    seqId=None)

    with pytest.raises(OperationError) as ex_info:
        looper.run(
            public_repo.submitSchema(schema)
        )
        ex_info.match("attr_names in schema can not be empty")  # This line is unreachable in case of an exception


def test_get_schema(submitted_schema, public_repo, looper):
    key = submitted_schema.getKey()
    schema = looper.run(public_repo.getSchema(ID(schemaKey=key)))
    assert schema == submitted_schema


def test_get_schema_by_seqno(submitted_schema, public_repo, looper):
    schema = looper.run(public_repo.getSchema(
        ID(schemaId=submitted_schema.seqId)))
    assert schema == submitted_schema


def test_get_schema_by_invalid_seqno(submitted_schema, public_repo, looper):
    with pytest.raises(SchemaNotFoundError):
        looper.run(public_repo.getSchema(
            ID(schemaId=(submitted_schema.seqId + randint(100, 1000)))))


def test_get_schema_non_existent(submitted_schema, public_repo, looper):
    key = submitted_schema.getKey()
    key = key._replace(name=key.name + randomString(5))
    with pytest.raises(SchemaNotFoundError):
        looper.run(public_repo.getSchema(ID(schemaKey=key)))
