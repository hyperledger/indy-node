import pytest
from scripts.performance.perf_gen_req_parser import ReqTypeParser
from scripts.performance.perf_processes import TestRunner
from scripts.performance.test.conftest import RGTestReq, LoadClientTest


ReqTypeParser._supported_requests = {"test_test": RGTestReq}


def test_valid_clients_num(tmpdir):
    LoadClientTest.clients = 0

    tr = TestRunner(clients=10, genesis_path="", seed="", req_kind="test_test",
                    batch_size=1, refresh_rate=10, buff_req=0, out_dir=tmpdir, val_sep="|",
                    wallet_key="", mode="t", pool_config='', sync_mode="one",
                    load_rate=10, out_file="output", load_time=1, client_runner=LoadClientTest.run)
    tr.test_run()

    assert LoadClientTest.clients == 10
    LoadClientTest.clients = 0


def test_load_one(tmpdir):
    LoadClientTest.reqs_snd = 0
    tr = TestRunner(clients=3, genesis_path="", seed="", req_kind="test_test",
                    batch_size=1, refresh_rate=10, buff_req=1, out_dir=tmpdir, val_sep="|",
                    wallet_key="", mode="t", pool_config='', sync_mode="one",
                    load_rate=10, out_file="output", load_time=2, client_runner=LoadClientTest.run)

    tr.test_run()

    assert LoadClientTest.reqs_snd == 20
    LoadClientTest.reqs_snd = 0


def test_load_all(tmpdir):
    LoadClientTest.reqs_snd = 0
    tr = TestRunner(clients=3, genesis_path="", seed="", req_kind="test_test",
                    batch_size=1, refresh_rate=10, buff_req=1, out_dir=tmpdir, val_sep="|",
                    wallet_key="", mode="t", pool_config='', sync_mode="all",
                    load_rate=10, out_file="output", load_time=2, client_runner=LoadClientTest.run)

    tr.test_run()

    assert LoadClientTest.reqs_snd == 60
    LoadClientTest.reqs_snd = 0
