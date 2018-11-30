from indy_node.utils.node_control_utils import NodeControlUtil


VERBOSE_OUTPUT =\
'''"Hardware":    
     "HDD_all":      27028 Mbs 
     "RAM_all_free":  2201 Mbs  
     "RAM_used_by_node":  845 Mbs   
"Node_info":   
     "BLS_key":      p2LdkcuVLnqidf9PAM1josFLfSTSTYuGqaSBx2Dq72Z5Kt2axQicYyqkQ6ZfcwzHpmLevmcXVwD4EC32wTbusvYxb5D1MJBfu67SQqxRTcK7pRBQXYiaPrzqUo9odhAgrwNPSbHcBJM6s5cNUPvjZZDuSJvhjC7tKFV9FGqyX4Zs4u
     "Catchup_status": 
          "Last_txn_3PC_keys": 
               "0":           
               "1":           
               "2":           
          "Ledger_statuses": 
               "0":            synced    
               "1":            synced    
               "2":            synced    
          "Number_txns_in_catchup": 
               "0":            0         
               "1":            0         
               "2":            0         
          "Received_LedgerStatus":            
          "Waiting_consistency_proof_msgs": 
               "0":            None      
               "1":            None      
               "2":            None      
     "Client_ip":    127.0.0.1 
     "Client_port":  6847      
     "Client_protocol":  tcp       
     "Committed_ledger_root_hashes": 
          "0":            b'5ddvDbJSFkbdMQ9mxTvXcb4iX19ZnA7tW8JJXi4ahneM'
          "1":            b'6fuCqGEa7q9rFFF2ULPpqtq52Y1HuKZ2x5QVLcRpHVRq'
          "2":            b'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn'
     "Committed_state_root_hashes": 
          "0":            b'GjP1Y4izxmZotD1DkoQeiTAm7KUkQW4CADb69wy3V2Go'
          "1":            b'9iemGdmHQr2b5CYpDGGDTRFxJ6VHEiTE4PFqFNAyQtca'
          "2":            b'DfNLmH4DAHTKv63YPFJzuRdeEtVwF5RtVnvKYHd8iLEA'
     "Count_of_replicas":  2         
     "Metrics":     
          "Delta":        0.1       
          "Lambda":       240       
          "Omega":        20        
          "average-per-second": 
               "read-transactions":  0.0       
               "write-transactions":  0.0       
          "avg backup throughput":  None      
          "client avg request latencies": 
               "0":            None      
               "1":            None      
          "instances started": 
               "0":            342796.144845116
               "1":            342796.144967239
          "master throughput":  None      
          "master throughput ratio":  None      
          "max master request latencies":  0         
          "ordered request counts": 
               "0":            0         
               "1":            0         
          "ordered request durations": 
               "0":            0         
               "1":            0         
          "throughput":  
               "0":            None      
               "1":            None      
          "total requests":  0         
          "transaction-count": 
               "config":       0         
               "ledger":       12        
               "pool":         4         
          "uptime":       5         
     "Mode":         participating
     "Name":         Alpha     
     "Node_ip":      127.0.0.1 
     "Node_port":    6846      
     "Node_protocol":  tcp       
     "Replicas_status": 
          "Alpha:0":     
               "Last_ordered_3PC": 
                     0         
                     0         
               "Primary":      Alpha:0   
               "Stashed_txns": 
                    "Stashed_PrePrepare":  0         
                    "Stashed_checkpoints":  0         
               "Watermarks":   0:300     
          "Alpha:1":     
               "Last_ordered_3PC": 
                     0         
                     0         
               "Primary":      Beta:1    
               "Stashed_txns": 
                    "Stashed_PrePrepare":  0         
                    "Stashed_checkpoints":  0         
               "Watermarks":   0:300     
     "Uncommitted_ledger_root_hashes": 
     "Uncommitted_ledger_txns": 
          "0":           
               "Count":        0         
          "1":           
               "Count":        0         
          "2":           
               "Count":        0         
     "Uncommitted_state_root_hashes": 
          "0":            b'GjP1Y4izxmZotD1DkoQeiTAm7KUkQW4CADb69wy3V2Go'
          "1":            b'9iemGdmHQr2b5CYpDGGDTRFxJ6VHEiTE4PFqFNAyQtca'
          "2":            b'DfNLmH4DAHTKv63YPFJzuRdeEtVwF5RtVnvKYHd8iLEA'
     "View_change_status": 
          "IC_queue":    
          "Last_complete_view_no":  0         
          "Last_view_change_started_at":  1970-01-01 00:00:00
          "VCDone_queue": 
               "Alpha":       
                     Alpha     
                     [[0, 4, '5ddvDbJSFkbdMQ9mxTvXcb4iX19ZnA7tW8JJXi4ahneM'], [1, 12, '6fuCqGEa7q9rFFF2ULPpqtq52Y1HuKZ2x5QVLcRpHVRq'], [2, 0, 'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn']]
               "Beta":        
                     Alpha     
                     [[0, 4, '5ddvDbJSFkbdMQ9mxTvXcb4iX19ZnA7tW8JJXi4ahneM'], [1, 12, '6fuCqGEa7q9rFFF2ULPpqtq52Y1HuKZ2x5QVLcRpHVRq'], [2, 0, 'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn']]
               "Delta":       
                     Alpha     
                     [[0, 4, '5ddvDbJSFkbdMQ9mxTvXcb4iX19ZnA7tW8JJXi4ahneM'], [1, 12, '6fuCqGEa7q9rFFF2ULPpqtq52Y1HuKZ2x5QVLcRpHVRq'], [2, 0, 'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn']]
               "Gamma":       
                     Alpha     
                     [[0, 4, '5ddvDbJSFkbdMQ9mxTvXcb4iX19ZnA7tW8JJXi4ahneM'], [1, 12, '6fuCqGEa7q9rFFF2ULPpqtq52Y1HuKZ2x5QVLcRpHVRq'], [2, 0, 'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn']]
          "VC_in_progress":  False     
          "View_No":      0         
     "did":          JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ
     "verkey":       3Syux6kKmqgZ4shG4dPDSAchKQwdHcfQbrpZcoxXz4fsoZftBrTypWP
"Pool_info":   
     "Blacklisted_nodes": 
     "Quorums":      {'timestamp': Quorum(2), 'checkpoint': Quorum(2), 'ledger_status_last_3PC': Quorum(2), 'observer_data': Quorum(2), 'same_consistency_proof': Quorum(2), 'strong': Quorum(3), 'weak': Quorum(2), 'bls_signatures': Quorum(3), 'f': 1, 'consistency_proof': Quorum(2), 'election': Quorum(3), 'view_change': Quorum(3), 'commit': Quorum(3), 'prepare': Quorum(2), 'ledger_status': Quorum(2), 'propagate': Quorum(2), 'backup_instance_faulty': Quorum(2), 'propagate_primary': Quorum(2), 'reply': Quorum(2), 'view_change_done': Quorum(3)}
     "Reachable_nodes": 
           ['Alpha', 0]
           ['Beta', 1]
           ['Delta', None]
           ['Gamma', None]
     "Reachable_nodes_count":  4         
     "Read_only":    False     
     "Suspicious_nodes":            
     "Total_nodes_count":  4         
     "Unreachable_nodes": 
     "Unreachable_nodes_count":  0         
     "f_value":      1         
"Protocol":    
"Software":    
     "Indy_packages": 
           ii  libindy                               1.6.1~701                                  amd64        This is the official SDK for Hyperledger Indy, which provides a
           ii  libindy-crypto                        0.4.5~23                                   amd64        This is the shared crypto libirary for Hyperledger Indy components.
                     
     "Installed_packages": 
           indy-plenum-dev 1.6
           yapf 0.21.0
           wrapt 1.10.11
           wheel 0.29.0
           ujson 1.33
           timeout-decorator 0.3.3
           snap 0.5  
           six 1.11.0
           setuptools 40.6.2
           semver 2.7.9
           pyzmq 17.0.0
           PyYAML 3.13
           python-rocksdb 0.6.9
           python-dateutil 2.6.1
           pytest 4.0.1
           pytest-xdist 1.16.0
           pytest-runner 2.11.1
           pytest-asyncio 0.9.0
           pyparsing 2.2.0
           pyorient 1.5.5
           Pympler 0.5
           pylint 1.8.1
           pyflakes 1.6.0
           pycodestyle 2.3.1
           py 1.7.0  
           psutil 5.4.3
           pluggy 0.8.0
           pkg-resources 0.0.0
           pip 9.0.3 
           pathlib2 2.3.2
           parso 0.2.0
           packaging 16.8
           numpy 1.12.1
           mysqlclient 1.3.12
           msgpack-python 0.4.6
           more-itertools 4.3.0
           migrate 0.3.8
           mccabe 0.6.1
           libnacl 1.6.1
           lazy-object-proxy 1.3.1
           jsonpickle 0.9.6
           jedi 0.12.0
           isort 4.2.15
           intervaltree 2.1.0
           indy-crypto 0.4.5
           flake8 3.5.0
           execnet 1.4.1
           Cython 0.25.2
           Charm-Crypto 0.0.0
           base58 1.0.0
           autopep8 1.3.5
           attrs 18.2.0
           atomicwrites 1.2.1
           async-generator 1.10
           astroid 1.6.0
           appdirs 1.4.3
           apipkg 1.4
           leveldb 0.194
           sha3 0.2.1
           rlp 0.5.1 
           crypto 1.4.1
           shellescape 3.4.1
           Naked 0.1.31
           requests 2.14.2
           sortedcontainers 1.5.7
           orderedset 2.0
           ioflo 1.5.4
           Pygments 2.2.0
           prompt-toolkit 0.57
           wcwidth 0.1.7
           raet 0.6.7
           portalocker 0.5.7
           indy-perf-load 1.1.1
     "OS_version":   Linux-4.15.0-39-generic-x86_64-with-Ubuntu-18.04-bionic
     "indy-node":    1.6       
     "sovrin":       unknown   
"Update time":  Friday, November 30, 2018 2:13:04 PM +0300
"response-version":  0.0.1     
"timestamp":    1543576384


"Configuration": 
     "Config":      
          "Main_config": 
                # Current network
                NETWORK_NAME = 'sandbox'
                          
                # Disable stdout logging
                enableStdOutLogging = False
                          
                # Directory to store ledger.
                LEDGER_DIR = '/var/lib/indy'
                          
                # Directory to store logs.
                LOG_DIR = '/var/log/indy'
                          
                # Directory to store keys.
                KEYS_DIR = '/var/lib/indy'
                          
                # Directory to store genesis transactions files.
                GENESIS_DIR = '/var/lib/indy'
                          
                # Directory to store backups.
                BACKUP_DIR = '/var/lib/indy/backup'
                          
                # Directory to store plugins.
                PLUGINS_DIR = '/var/lib/indy/plugins'
                          
                # Directory to store node info.
                NODE_INFO_DIR = '/var/lib/indy'
                          
          "Network_config": 
          "User_config": 
     "Genesis_txns": 
          "domain_txns": 
                {"reqSignature":{},"txn":{"data":{"alias":"Steward1","dest":"MSjKTWkPLtYoPEaTF1TUDb","role":"2","verkey":"~Jh3HbbPXi3YAV8d9NAvya1"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{"seqNo":1},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Steward2","dest":"E4rYSWBUA12j5ScG6mie1p","role":"2","verkey":"~5VNintF7vai7kGfka5wNUs"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{"seqNo":2},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Steward3","dest":"QxzxUA7gePtb9t46n1YgsC","role":"2","verkey":"~3mXRFPw4UcwWBibqNTAwSu"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{"seqNo":3},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Steward4","dest":"WMStfRmANynUmdpa1QYKDw","role":"2","verkey":"~PahRAsP3gEiYDPWbq9a32a"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{"seqNo":4},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Trs0","dest":"M9BJDuS24bqbJNvBRsoGg3","role":"0","verkey":"~T4jcZyPoQcgZrk4V8HAwmS"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Trs1","dest":"E7QRhdcnhAwA6E46k9EtZo","role":"0","verkey":"~6J6t6L22p6exo1RZuE45M7"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Trs2","dest":"CA4bVFDU4GLbX8xZju811o","role":"0","verkey":"~BzuoCRKBSjeCbmEXME6AXq"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Trs3","dest":"B8fV7naUqLATYocqu7yZ8W","role":"0","verkey":"~5sF3ouhzFsfmHfFw7EHJCf"},"metadata":{},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Jason","dest":"6g1u9vpX1qPn8YBjWvtu4c","verkey":"~AsnCAVfzrKWHP3TV6MCF3b"},"metadata":{"from":"5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC"},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Alice","dest":"6ouriXMZkLeHsuXrN1X1fd","verkey":"~JMS1SU8mTNzGWcu5TjJJgn"},"metadata":{"from":"5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC"},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"John","dest":"6QQrVjXpuuN6b9ZMLzcxrF","verkey":"~WinSTs9xbDzxPYXtmjqL2E"},"metadata":{"from":"5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC"},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"alias":"Les","dest":"7WVJxbpefaGYGkNTxBkCTn","verkey":"~LLRoZgS7JeC2putNxWFTC1"},"metadata":{"from":"5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC"},"protocolVersion":2,"type":"1"},"txnMetadata":{},"ver":"1"}\r
                          
          "pool_txns":   
                {"reqSignature":{},"txn":{"data":{"data":{"alias":"Alpha","blskey":"p2LdkcuVLnqidf9PAM1josFLfSTSTYuGqaSBx2Dq72Z5Kt2axQicYyqkQ6ZfcwzHpmLevmcXVwD4EC32wTbusvYxb5D1MJBfu67SQqxRTcK7pRBQXYiaPrzqUo9odhAgrwNPSbHcBJM6s5cNUPvjZZDuSJvhjC7tKFV9FGqyX4Zs4u","blskey_pop":"QuMqWAAzv7qGbJiFUnd3iAagoAXvg5VvCzABJqn4KJUEWwtSDF5mkGPpDeVFayPvG5RL8HWbnBdy84knPbUP6e5tmZb4KvsFxZ5QU7ytkPf3VFR8eue8DUK6hmvVj7BMtsrPAALPtwi44wX9AhdhNJp882Qh4yeyQqyWiSaa7Lgp3h","client_ip":"127.0.0.1","client_port":6847,"node_ip":"127.0.0.1","node_port":6846,"services":["VALIDATOR"]},"dest":"JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ"},"metadata":{"from":"MSjKTWkPLtYoPEaTF1TUDb"},"protocolVersion":2,"type":"0"},"txnMetadata":{"seqNo":1,"txnId":"b1a96dd646bccaa24cef7a3db22a6f995f05658f4f1c3272913e258c03e6fb24"},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"data":{"alias":"Beta","blskey":"2JY8jXAiy3ffLu1ggSaiFTBpmb9X7wUZEedg7G3mJSU1vCnqFzYAofGR9SGEvb1C3p88Kdm2CPAdMyMc5v9KxL26vfeeHzRa2N5EHwV1JpPH5kcdYYkFhgNf8wxFAvJ9vPS1aCVms41ZC17GeovJLh4L2iACNd7ttPyS5M6a9Uux9oz","blskey_pop":"Qwd3DnqnMBSBMqd7fMhMteciUfrPFAooyV55tDC2vduyRnvyxJuzmiXNxUgL7xr9w9GnxEjeSEcGKhDgUE3fK5z3cbUAgPrJGoSac9uHRPzmLpXUffQAqN6tHYGcJB6jmvU1931G9gZb2Tvi9ifeRfZFX9KbfUosMW8boBuCn1bjNf","client_ip":"127.0.0.1","client_port":6849,"node_ip":"127.0.0.1","node_port":6848,"services":["VALIDATOR"]},"dest":"DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2"},"metadata":{"from":"E4rYSWBUA12j5ScG6mie1p"},"protocolVersion":2,"type":"0"},"txnMetadata":{"seqNo":2,"txnId":"703390318bd55aef50b7823d2b90a846debff99e6e3d401a24a921b733912a6d"},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"data":{"alias":"Gamma","blskey":"1JwRChBPGQTtp4m4aNBRrf2kG3mzgxtRUTAscx8iV9uDih34pKWnEA54CoNq3DhAgEURQCN6VKrSZUb6zzzLBHhQt7HBdw2kbfUR3Fap2jqE6TEDamFQpqced2GRVcDo5wgVVKydsf1rFundAk7jMSk7mLrf7zBBN9xBx2yaUkvueN","blskey_pop":"RFNH8Q3PJqkTuxHge7CE8hCWkEWNpESR9nZ8uvpW4QNwS2LFcC3L8qsQQEtYxJTJXGhnc4qKS48YwSC1Nyz82BoWtkyFqiAfWWpsA2xn4ykHjvKY2d5YKYGmxLoPB2tVmsqkWa3dpYDSUymdjudeNqV84tsnZbcr9de3vwCcqTvavs","client_ip":"127.0.0.1","client_port":6851,"node_ip":"127.0.0.1","node_port":6850,"services":["VALIDATOR"]},"dest":"AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3"},"metadata":{"from":"QxzxUA7gePtb9t46n1YgsC"},"protocolVersion":2,"type":"0"},"txnMetadata":{"seqNo":3,"txnId":"a8ab3d5805c9214bc66b794f599cbccd5a5958dc5a6a322ee81e3a68344c6db7"},"ver":"1"}\r
                {"reqSignature":{},"txn":{"data":{"data":{"alias":"Delta","blskey":"4kkk7y7NQVzcfvY4SAe1HBMYnFohAJ2ygLeJd3nC77SFv2mJAmebH3BGbrGPHamLZMAFWQJNHEM81P62RfZjnb5SER6cQk1MNMeQCR3GVbEXDQRhhMQj2KqfHNFvDajrdQtyppc4MZ58r6QeiYH3R68mGSWbiWwmPZuiqgbSdSmweqc","blskey_pop":"RLp7PsVA8kJkXcMfvsCqcsuntcpzMg2DKF2RdWfu14GjhdPQ8B4Gsc7t6ZFWfYf3qG58JBsCLBLZDd8Ns1itVkZQuzJwejKLi5kY6xTBtR6SyyQ48mBQtyF9rryGhAu3dExqkXGCZHmyNBpndF9XCsJh6K7VB33S2G1gHiJQ4rg4Ky","client_ip":"127.0.0.1","client_port":6853,"node_ip":"127.0.0.1","node_port":6852,"services":["VALIDATOR"]},"dest":"4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2"},"metadata":{"from":"WMStfRmANynUmdpa1QYKDw"},"protocolVersion":2,"type":"0"},"txnMetadata":{"seqNo":4,"txnId":"18833da39fb9b7f8c917fe0220daf9cf12e6524df8fb16e39f04dbe827e2d200"},"ver":"1"}\r
                          
     "indy-node-control.service": 
     "indy-node.service": 
     "indy.env":               
     "iptables_config": 
     "node_control.conf":'''


def test_vi_verbose_output():
    out = NodeControlUtil.run_shell_command("validator-info -v --basedir .")
    assert out == VERBOSE_OUTPUT
