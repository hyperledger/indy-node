import pytest

from perf_load.perf_gen_req_parser import ReqTypeParser
from perf_load.perf_req_gen_seq import RGSeqReqs
from perf_load.perf_req_gen_nym import RGNym, RGGetNym
from perf_load.perf_req_gen_schema import RGSchema, RGGetSchema
from perf_load.perf_req_gen_attrib import RGAttrib, RGGetAttrib
from perf_load.perf_req_gen_definition import RGGetDefinition, RGDefinition
from perf_load.perf_req_gen_revoc import RGDefRevoc, RGGetDefRevoc, RGEntryRevoc, RGGetEntryRevoc, RGGetRevocRegDelta
from perf_load.perf_req_gen_payment import RGGetPaymentSources, RGPayment, RGVerifyPayment

from perf_load.perf_req_gen_fees import RGGetFees
from perf_load.perf_req_gen_get_taa import RGGetTAA
from perf_load.perf_req_gen_get_taa_aml import RGGetTAAAML
from perf_load.perf_req_gen_get_auth_rules import RGGetAuthRules


def test_supported_reqs():
    reqs = ReqTypeParser.supported_requests()
    assert isinstance(reqs, list)
    assert reqs
    should_support = ["nym", "schema", "attrib", "cred_def", "revoc_reg_def", "revoc_reg_entry", "get_nym",
                      "get_attrib", "get_schema", "get_cred_def", "get_revoc_reg_def", "get_revoc_reg",
                      "get_revoc_reg_delta", "get_payment_sources", "payment", "verify_payment",
                      "get_fees", "cfg_writes", "demoted_node", "get_txn", "get_taa", "get_taa_aml", "get_auth_rule"]
    assert len(reqs) == len(should_support)
    for ss in should_support:
        assert ss in reqs


@pytest.mark.parametrize("kind,exp_type",
                         [("nym", RGNym), ("schema", RGSchema), ("attrib", RGAttrib), ("cred_def", RGDefinition),
                          ("revoc_reg_def", RGDefRevoc), ("revoc_reg_entry", RGEntryRevoc), ("get_nym", RGGetNym),
                          ("get_attrib", RGGetAttrib), ("get_schema", RGGetSchema), ("get_cred_def", RGGetDefinition),
                          ("get_revoc_reg_def", RGGetDefRevoc), ("get_revoc_reg", RGGetEntryRevoc),
                          ("get_revoc_reg_delta", RGGetRevocRegDelta), ("get_payment_sources", RGGetPaymentSources),
                          ("payment", RGPayment), ("verify_payment", RGVerifyPayment), ("get_fees", RGGetFees),
                          ("get_taa", RGGetTAA), ("get_taa_aml", RGGetTAAAML), ("get_auth_rule", RGGetAuthRules)])
def test_parse_simple(kind, exp_type):
    r = ReqTypeParser.create_req_generator(kind)
    assert r[0] == exp_type
    assert r[1] == {'label': kind}


@pytest.mark.parametrize("req,exp",
                         [('{"nym": 3}', (RGNym, {'label': "nym", "count": 3})),
                          ('{"nym": {"label": "nym1"}}', (RGNym, {'label': "nym1"})),
                          ('{"t1": "nym"}', (RGNym, {"label": "t1"})),
                          ('{"t3": {"nym": 4}}', (RGNym, {"label": "t3", "count": 4})),
                          ('{"t2": {"nym": {"label": "nym2", "count": 1}}}', (RGNym, {'label': "t2", "count": 1}))])
def test_parse_json_obj(req, exp):
    r = ReqTypeParser.create_req_generator(req)
    assert r[0] == exp[0]
    assert r[1] == exp[1]


@pytest.mark.parametrize(
    "req,exp",
    [('["nym", "schema"]',
      (RGSeqReqs, {"next_random": False, "reqs": [(RGNym, {'label': "nym"}), (RGSchema, {'label': "schema"})]})),
     ('[{"nym": 2}, "schema"]',
      (RGSeqReqs, {"next_random": False, "reqs": [(RGNym, {'label': "nym", "count": 2}), (RGSchema, {'label': "schema"})]})),
     ('[{"nym": 2}, {"schema": 4}]',
      (RGSeqReqs, {"next_random": False, "reqs": [(RGNym, {'label': "nym", "count": 2}), (RGSchema, {'label': "schema", "count": 4})]})),
     ('[{"nym": {"label": "nym1", "count": 2}}, {"t1": "schema"}]',
      (RGSeqReqs, {"next_random": False, "reqs": [(RGNym, {'label': "nym1", "count": 2}), (RGSchema, {'label': "t1"})]})),
     ('[{"t3": {"nym": 4}}, "attrib", {"t4": {"schema": {"count": 6}}}]',
      (RGSeqReqs, {"next_random": False, "reqs": [(RGNym, {'label': "t3", "count": 4}), (RGAttrib, {'label': 'attrib'}), (RGSchema, {'label': "t4", "count": 6})]}))])
def test_parse_json_seq_seq(req, exp):
    r = ReqTypeParser.create_req_generator(req)
    assert r[0] == exp[0]
    assert r[1] == exp[1]


@pytest.mark.parametrize(
    "req,exp",
    [('{"nym": 3, "schema": 7}',
      (RGSeqReqs, {"next_random": True, "reqs": [(RGNym, {'label': "nym", "count": 3}), (RGSchema, {'label': "schema", "count": 7})]})),
     ('{"nym": {"label": "nym1", "count": 2}, "t1": "schema"}',
      (RGSeqReqs, {"next_random": True, "reqs": [(RGNym, {'label': "nym1", "count": 2}), (RGSchema, {'label': "t1"})]})),
     ('{"t3": {"nym": 4}, "attrib": 3, "t4": {"schema": {"count": 6}}}',
      (RGSeqReqs, {"next_random": True, "reqs": [(RGNym, {'label': "t3", "count": 4}), (RGAttrib, {'label': 'attrib', "count": 3}), (RGSchema, {'label': "t4", "count": 6})]}))])
def test_parse_json_seq_rand(req, exp):
    r = ReqTypeParser.create_req_generator(req)
    assert r[0] == exp[0]
    assert r[1]["next_random"] == exp[1]["next_random"]
    assert sorted(r[1]["reqs"], key=lambda x: str(x[0])) == sorted(exp[1]["reqs"], key=lambda x: str(x[0]))
