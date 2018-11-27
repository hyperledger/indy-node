# TODO more tests

testinfra_hosts = ['clients']

pool_name = "indy-pool"


def test_pool_txns_genesis_file_exists(host):
    txns_file = host.file("{}/pool_transactions_genesis".format(host.user().home))
    assert txns_file.exists


def test_cli_is_configured(host):
    # XXX indy-cli won't return non-zero if can't connect
    res = host.run("echo 'pool connect %s' | indy-cli", pool_name)
    assert 'Pool "{}" has been connected'.format(pool_name) in res.stdout
