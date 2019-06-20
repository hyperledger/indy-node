import pytest

from plenum.common.exceptions import RequestNackedException

from indy_node.test.state_proof.test_state_proof_for_get_requests import check_get_delta

from indy_node.test.anon_creds.conftest import send_revoc_reg_entry, send_revoc_reg_def, send_claim_def, claim_def
from indy_node.test.schema.test_send_get_schema import send_schema_req
from indy_node.test.state_proof.conftest import nodeSetWithOneNodeResponding


def test_state_proof_returned_for_get_revoc_reg_delta(looper,
                                                      nodeSetWithOneNodeResponding,
                                                      sdk_wallet_steward,
                                                      sdk_pool_handle,
                                                      sdk_wallet_client,
                                                      send_revoc_reg_entry):
    revoc_reg_def = send_revoc_reg_entry[0]
    revoc_reg_entry_data = send_revoc_reg_entry[1][0]['operation']
    timestamp = send_revoc_reg_entry[1][1]['result']['txnMetadata']['txnTime']

    with pytest.raises(RequestNackedException, match='Timestamp FROM more then TO'):
        check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp + 1, timestamp,
                        sdk_pool_handle, revoc_reg_entry_data)
