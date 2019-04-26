from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from plenum.test.helper import sdk_multi_sign_request_objects, sdk_send_signed_requests, sdk_get_and_check_replies


def send_and_check(test_body: AbstractTest, req):
    signed_reqs = sdk_multi_sign_request_objects(test_body.looper,
                                                 [test_body.trustee_wallet],
                                                 [req])
    request_couple = sdk_send_signed_requests(test_body.sdk_pool_handle,
                                              signed_reqs)[0]

    return sdk_get_and_check_replies(test_body.looper, [request_couple])[0]