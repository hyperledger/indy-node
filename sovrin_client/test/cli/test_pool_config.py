import pytest

from sovrin_node.test.upgrade.conftest import validUpgrade
from sovrin_client.test.cli.constants import INVALID_SYNTAX


def testPoolConfigInvalidSyntax(be, do, trusteeCli):
    be(trusteeCli)
    do('send POOL_CONFIG wites=True force=False', expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=Tue force=False', expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=True froce=False', expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=True force=1', expect=INVALID_SYNTAX, within=10)


def testPoolConfigWritableFalse(be, do, trusteeCli):
    be(trusteeCli)
    do('send POOL_CONFIG writes=False force=False', expect="Pool config successful", within=10)
    do('send NYM dest=33333333333333333333333333333333333333333333', expect="Pool is in readonly mode", within=10)


def testPoolConfigWritableTrue(be, do, trusteeCli):
    be(trusteeCli)
    do('send NYM dest=33333333333333333333333333333333333333333333', expect="Pool is in readonly mode", within=10)
    do('send POOL_CONFIG writes=True force=False', expect="Pool config successful", within=10)
    do('send NYM dest=33333333333333333333333333333333333333333333', expect="added", within=10)
