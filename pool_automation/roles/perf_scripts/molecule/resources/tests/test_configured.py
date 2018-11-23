testinfra_hosts = ['clients']

def test_pool_txns_genesis_file_exists(host):
    txns_file = host.file("{}/pool_transactions_genesis".format(host.user().home))
    assert txns_file.exists

#def test_perf_processes_can_connect(host):
#    res = host.run("perf_processes.py -g ./txns -c 100 -n 10")
