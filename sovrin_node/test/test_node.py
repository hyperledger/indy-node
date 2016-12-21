from sovrin_node.node import Node
from sovrin_client.client import Client


def testNode():
    n1 = Node()
    assert n1 is not None


def testClient():
    n1 = Node()
    c1 = Client()
    n1.dummy()
    c1.dummy()

