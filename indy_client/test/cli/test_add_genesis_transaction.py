import json

from plenum.common.constants import VERKEY, DATA, NODE, TYPE
from plenum.common.txn_util import get_payload_data, get_type
from plenum.test.cli.helper import checkCmdValid

from indy_common.constants import NYM
from indy_common.constants import TARGET_NYM, ROLE
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions


def executeAndCheckGenTxn(cli, cmd, typ, nym, role=None, data=None):
    checkCmdValid(cli, cmd)
    nymCorrect = False
    roleCorrect = False if role else True
    dataCorrect = False if data else True
    typeCorrect = False if typ else True

    role = Roles[role].value if role else role
    for txn in cli.genesisTransactions:
        txn_data = get_payload_data(txn)
        if txn_data.get(TARGET_NYM) == nym:
            nymCorrect = True
            if get_type(txn) == typ:
                typeCorrect = True
            if txn_data.get(ROLE) == role:
                roleCorrect = True
            if data and txn_data.get(DATA) == json.loads(data):
                dataCorrect = True

    assert typeCorrect and nymCorrect and roleCorrect and dataCorrect
    assert "Genesis transaction added" in cli.lastCmdOutput


def prepareCmdAndCheckGenTxn(
        cli, typ: IndyTransactions, nym, role=None, data=None):
    cmd = "add genesis transaction {} dest={}".format(typ.name, nym)
    if role:
        cmd += " role={}".format(role)
    if data:
        cmd += " with data {}".format(data)
    executeAndCheckGenTxn(cli, cmd, typ.value, nym, role, data)


def testAddGenTxnBasic(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    role = None
    typ = IndyTransactions.NYM
    prepareCmdAndCheckGenTxn(cli, typ, nym, role)


def testAddGenTxnWithRole(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    role = Roles.STEWARD.name
    typ = IndyTransactions.NYM
    prepareCmdAndCheckGenTxn(cli, typ, nym, role)


def testAddGenTxnForNode(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    by = "FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW"
    role = None
    typ = NODE
    data = '{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}'
    cmd = 'add genesis transaction {} for {} by {} with data {}'.format(
        typ, nym, by, data)
    executeAndCheckGenTxn(cli, cmd, typ, nym, role, data)
