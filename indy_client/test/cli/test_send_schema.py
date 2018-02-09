from indy_client.test.cli.constants import SCHEMA_ADDED, SCHEMA_NOT_ADDED_DUPLICATE


def test_send_schema_multiple_attribs(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)


def test_send_schema_one_attrib(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree2 version=1.1 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)


def test_can_not_send_same_schema(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree3 version=1.3 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)
    do('send SCHEMA name=Degree3 version=1.3 keys=attrib1',
       expect=SCHEMA_NOT_ADDED_DUPLICATE, within=5)
