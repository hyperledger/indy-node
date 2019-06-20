import json
from perf_load.perf_req_gen_seq import RGSeqReqs
from perf_load.perf_req_gen_nym import RGNym, RGGetNym
from perf_load.perf_req_gen_schema import RGSchema, RGGetSchema
from perf_load.perf_req_gen_attrib import RGAttrib, RGGetAttrib
from perf_load.perf_req_gen_definition import RGGetDefinition, RGDefinition
from perf_load.perf_req_gen_revoc import RGDefRevoc, RGGetDefRevoc, RGEntryRevoc, RGGetEntryRevoc, RGGetRevocRegDelta
from perf_load.perf_req_gen_payment import RGGetPaymentSources, RGPayment, RGVerifyPayment
from perf_load.perf_req_gen_cfg_writes import RGConfigChangeState
from perf_load.perf_req_gen_demoted_node import RGPoolNewDemotedNode
from perf_load.perf_req_gen_get_txn import RGGetTxn
from perf_load.perf_req_gen_get_taa import RGGetTAA
from perf_load.perf_req_gen_get_taa_aml import RGGetTAAAML
from perf_load.perf_req_gen_get_auth_rules import RGGetAuthRules
from perf_load.perf_req_gen_fees import RGGetFees


class ReqTypeParser:
    _supported_requests = \
        {"nym": RGNym, "schema": RGSchema, "attrib": RGAttrib, "cred_def": RGDefinition, "revoc_reg_def": RGDefRevoc,
         "revoc_reg_entry": RGEntryRevoc, "get_nym": RGGetNym, "get_attrib": RGGetAttrib, "get_schema": RGGetSchema,
         "get_cred_def": RGGetDefinition, "get_revoc_reg_def": RGGetDefRevoc, "get_revoc_reg": RGGetEntryRevoc,
         "get_revoc_reg_delta": RGGetRevocRegDelta, "get_payment_sources": RGGetPaymentSources, "payment": RGPayment,
         "verify_payment": RGVerifyPayment, "cfg_writes": RGConfigChangeState, "demoted_node": RGPoolNewDemotedNode,
         "get_txn": RGGetTxn, 'get_taa': RGGetTAA, 'get_taa_aml': RGGetTAAAML, 'get_auth_rule': RGGetAuthRules,
         "get_fees": RGGetFees}

    @classmethod
    def supported_requests(cls):
        return list(cls._supported_requests.keys())

    @classmethod
    def __add_label(cls, cls_name, param):
        ret_dict = param if param is not None else {}
        if isinstance(param, int):
            ret_dict = {}
            ret_dict["count"] = param
        lbl = [k for k, v in cls._supported_requests.items() if v == cls_name]
        if "label" not in ret_dict:
            ret_dict["label"] = lbl[0]
        return cls_name, ret_dict

    @classmethod
    def __parse_single(cls, req_kind, prms):
        if req_kind is None:
            return cls.__parse_single(prms, None)
        if isinstance(req_kind, str) and req_kind in cls._supported_requests:
            return cls.__add_label(cls._supported_requests[req_kind], prms)
        if isinstance(req_kind, str) and req_kind not in cls._supported_requests:
            ret_cls, ret_par = cls.__parse_single(None, prms)
            ret_par.update({"label": req_kind})
            return ret_cls, ret_par
        if isinstance(req_kind, dict) and len(req_kind.keys()) == 1:
            k = list(req_kind)[0]
            v = req_kind[k]
            return cls.__parse_single(k, v)
        raise RuntimeError("Invalid parameter format")

    @classmethod
    def create_req_generator(cls, req_kind_arg):
        if req_kind_arg in cls._supported_requests:
            return cls._supported_requests[req_kind_arg], {"label": req_kind_arg}
        try:
            reqs = json.loads(req_kind_arg)
        except Exception as e:
            raise RuntimeError("Invalid parameter format")

        ret_reqs = []
        randomizing = False
        if isinstance(reqs, dict):
            randomizing = True
            for k, v in reqs.items():
                ret_reqs.append(cls.__parse_single(k, v))
        elif isinstance(reqs, list):
            randomizing = False
            for r in reqs:
                ret_reqs.append(cls.__parse_single(r, {}))
        if len(ret_reqs) == 1:
            req = ret_reqs[0][0]
            return cls.__add_label(req, ret_reqs[0][1])
        else:
            return RGSeqReqs, {'next_random': randomizing, 'reqs': ret_reqs}
