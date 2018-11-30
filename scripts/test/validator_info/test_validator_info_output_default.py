from indy_node.utils.node_control_utils import NodeControlUtil


DEFAULT_OUTPUT =\
"""Validator Alpha is stopped
Update time:     Friday, November 30, 2018 2:13:04 PM +0300
Validator DID:    JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ
Verification Key: 3Syux6kKmqgZ4shG4dPDSAchKQwdHcfQbrpZcoxXz4fsoZftBrTypWP
BLS Key: p2LdkcuVLnqidf9PAM1josFLfSTSTYuGqaSBx2Dq72Z5Kt2axQicYyqkQ6ZfcwzHpmLevmcXVwD4EC32wTbusvYxb5D1MJBfu67SQqxRTcK7pRBQXYiaPrzqUo9odhAgrwNPSbHcBJM6s5cNUPvjZZDuSJvhjC7tKFV9FGqyX4Zs4u
Node HA:        127.0.0.1:6846
Client HA:      127.0.0.1:6847
Metrics:
  Uptime: 5 seconds
  Total config Transactions:  0
  Total ledger Transactions:  12
  Total pool Transactions:  4
  Read Transactions/Seconds:  0.00
  Write Transactions/Seconds: 0.00
Reachable Hosts:   4/4
  Alpha	(0)
  Beta	(1)
  Delta	
  Gamma	
Unreachable Hosts: 0/4
Software Versions:
  indy-node: 1.6
  sovrin: unknown"""


def test_vi_default_output():
    out = NodeControlUtil.run_shell_command("validator-info --basedir .")
    assert out == DEFAULT_OUTPUT
