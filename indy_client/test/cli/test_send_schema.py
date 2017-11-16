from indy_client.test.cli.constants import SCHEMA_ADDED


def testSendSchemaMultipleAttribs(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)


def testSendSchemaOneAttrib(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree2 version=1.1 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)
