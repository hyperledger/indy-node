"""
Created on Nov 8, 2017

@author: khoi.ngo

Containing test scripts of test scenario 11: special case for TrustAnchor role.
"""

# !/usr/bin/env python3.6
import json

from indy import ledger, signus

from libraries import common
from libraries.constant import seed_default_trustee
from libraries.constant import Role
from libraries.utils import perform, generate_random_string,\
                            perform_with_expected_code
from test_scripts.test_scenario_base import TestScenarioBase


class SpecialCaseTrustAnchorRole(TestScenarioBase):

    async def execute_test_steps(self):
        # Declare all values use in the test
        seed_trustee1 = generate_random_string(prefix="Trustee1", size=32)
        seed_trustee2 = generate_random_string(prefix="Trustee2", size=32)
        seed_steward1 = generate_random_string(prefix="Steward1", size=32)
        seed_steward2 = generate_random_string(prefix="Steward2", size=32)
        seed_trustanchor1 = generate_random_string(
            prefix="TrustAnchor1", size=32)
        seed_trustanchor2 = generate_random_string(
            prefix="TrustAnchor2", size=32)
        seed_trustanchor3 = generate_random_string(
            prefix="TrustAnchor3", size=32)
        # 1. Create ledger config from genesis txn file
        self.steps.add_step("Create and open pool Ledger")
        self.pool_handle, self.wallet_handle = await perform(
                                                self.steps,
                                                common.prepare_pool_and_wallet,
                                                self.pool_name,
                                                self.wallet_name,
                                                self.pool_genesis_txn_file,
                                                ignore_exception=False)

        # 2. Create DIDs ----------------------------------------------------
        self.steps.add_step("Create DIDs")
        (default_trustee_did, _) = await perform(
                                    self.steps, signus.create_and_store_my_did,
                                    self.wallet_handle,
                                    json.dumps({"seed": seed_default_trustee}))

        (trustee1_did, trustee1_verkey) = await perform(
                                          self.steps,
                                          signus.create_and_store_my_did,
                                          self.wallet_handle,
                                          json.dumps({"seed": seed_trustee1}))

        (trustee2_did, trustee2_verkey) = await perform(
                                          self.steps,
                                          signus.create_and_store_my_did,
                                          self.wallet_handle,
                                          json.dumps({"seed": seed_trustee2}))

        (steward1_did, steward1_verkey) = await perform(
                                          self.steps,
                                          signus.create_and_store_my_did,
                                          self.wallet_handle,
                                          json.dumps({"seed": seed_steward1}))

        (steward2_did, steward2_verkey) = await perform(
                                          self.steps,
                                          signus.create_and_store_my_did,
                                          self.wallet_handle,
                                          json.dumps({"seed": seed_steward2}))

        (trustanchor1_did, trustanchor1_verkey) = await perform(
                                    self.steps,
                                    signus.create_and_store_my_did,
                                    self.wallet_handle,
                                    json.dumps({"seed": seed_trustanchor1}))

        (trustanchor2_did, trustanchor2_verkey) = await perform(
                                    self.steps,
                                    signus.create_and_store_my_did,
                                    self.wallet_handle,
                                    json.dumps({"seed": seed_trustanchor2}))

        (trustanchor3_did, trustanchor3_verkey) = await perform(
                                    self.steps,
                                    signus.create_and_store_my_did,
                                    self.wallet_handle,
                                    json.dumps({"seed": seed_trustanchor3}))

        # 3. Using the default Trustee create a TrustAnchor and a new Trustee--
        self.steps.add_step("Use default Trustee to create a Trustee")
        await perform(self.steps, common.build_and_send_nym_request,
                      self.pool_handle, self.wallet_handle,
                      default_trustee_did, trustee1_did, trustee1_verkey,
                      None, Role.TRUSTEE)

        # 4. Verify GET_NYM for trustee1---------------------------------------
        self.steps.add_step("Verify get nym for Trustee")
        get_nym_txn_req4 = await perform(
                            self.steps, ledger.build_get_nym_request,
                            default_trustee_did, trustee1_did)
        await perform(self.steps, ledger.submit_request, self.pool_handle,
                      get_nym_txn_req4)

        # 5. Create TrustAnchor1
        self.steps.add_step("Create TrustAnchor1")
        await perform(self.steps, common.build_and_send_nym_request,
                      self.pool_handle, self.wallet_handle,
                      default_trustee_did, trustanchor1_did,
                      trustanchor1_verkey, None, Role.TRUST_ANCHOR)

        # 6. Verify GET_NYM for TrustAnchor1-----------------------------------
        self.steps.add_step("Verify GET_NYM for TrustAnchor1")
        get_nym_txn_req6 = await perform(
                            self.steps, ledger.build_get_nym_request,
                            default_trustee_did, trustanchor1_did)
        await perform(self.steps, ledger.submit_request, self.pool_handle,
                      get_nym_txn_req6)

        # 7. Using the TrustAnchor create a Trustee (Trust Anchor should not be
        self.steps.add_step("Use TrustAnchor1 to create a Trustee")
        await perform_with_expected_code(
            self.steps, common.build_and_send_nym_request, self.pool_handle,
            self.wallet_handle, trustanchor1_did, trustee2_did,
            trustee2_verkey, None, Role.TRUSTEE, expected_code=304)

        # 8. Verify GET_NYM for new Trustee------------------------------------
        self.steps.add_step("Verify get NYM for new trustee")
        get_nym_txn_req8 = await perform(
                            self.steps, ledger.build_get_nym_request,
                            trustanchor1_did, trustee2_did)
        await perform(self.steps, ledger.submit_request, self.pool_handle,
                      get_nym_txn_req8)

        # 9. Verify that the TestTrustAnchorTrustee cannot create a new Steward
        self.steps.add_step("Verify a trustee cannot create a new Steward")
        await perform_with_expected_code(
            self.steps, common.build_and_send_nym_request, self.pool_handle,
            self.wallet_handle, trustee2_did, steward1_did, steward1_verkey,
            None, Role.STEWARD, expected_code=304)

        # 10. Using the TrustAnchor blacklist a Trustee (TrustAnchor should not
        # be able to blacklist Trustee)
        self.steps.add_step("Use TrustAnchor to blacklist a Trustee")
        await perform_with_expected_code(
            self.steps, common.build_and_send_nym_request, self.pool_handle,
            self.wallet_handle, trustanchor1_did, trustee1_did,
            trustee1_verkey, None, Role.NONE, expected_code=304)

        # 11. Verify Trustee was not blacklisted by creating another Trustee---
        self.steps.add_step(
            "Verify Trustee was not blacklisted by creating another Trustee")
        await perform(self.steps, common.build_and_send_nym_request,
                      self.pool_handle, self.wallet_handle, trustee1_did,
                      trustee2_did, trustee2_verkey, None, Role.TRUSTEE)

        # 12. Using the TrustAnchor1 to create a Steward2 ---------------------
        self.steps.add_step("TrustAnchor1 cannot create a Steward2")
        await perform_with_expected_code(
                self.steps, common.build_and_send_nym_request,
                self.pool_handle, self.wallet_handle, trustanchor1_did,
                steward2_did, steward2_verkey, None, Role.STEWARD,
                expected_code=304)

        # 13. Using the Trustee1 create Steward1 ------------------------------
        self.steps.add_step("Using the Trustee1 create Steward1")
        await perform(self.steps, common.build_and_send_nym_request,
                      self.pool_handle, self.wallet_handle, trustee1_did,
                      steward1_did, steward1_verkey, None, Role.STEWARD)

        # 14. Now run the test to blacklist Steward1
        self.steps.add_step("Run the test to blacklist Steward1")
        await perform_with_expected_code(
                self.steps, common.build_and_send_nym_request,
                self.pool_handle, self.wallet_handle, trustanchor1_did,
                steward1_did, steward1_verkey, None, Role.NONE,
                expected_code=304)

        # 15. Verify that a TrustAnchor1 cannot create another TrustAnchor3 ---
        self.steps.add_step("Verify TrustAnchor1 cannot create a TrustAnchor3")
        await perform_with_expected_code(
                self.steps, common.build_and_send_nym_request,
                self.pool_handle, self.wallet_handle, trustanchor1_did,
                trustanchor3_did, trustanchor3_verkey, None, Role.TRUST_ANCHOR,
                expected_code=304)

        # 16. Using the Trustee1 create TrustAnchor2 --------------------------
        self.steps.add_step("Using the Trustee1 create Steward1")
        await perform(self.steps, common.build_and_send_nym_request,
                      self.pool_handle, self.wallet_handle,
                      trustee1_did, trustanchor2_did, trustanchor2_verkey,
                      None, Role.TRUST_ANCHOR)

        # 17. Verify that a TrustAnchor1 cannot blacklist another TrustAnchor2
        self.steps.add_step(
            "Verify TrustAnchor1 cannot blacklist TrustAnchor2")
        await perform_with_expected_code(
                self.steps, common.build_and_send_nym_request,
                self.pool_handle, self.wallet_handle, trustanchor1_did,
                trustanchor2_did, trustanchor2_verkey, None, Role.NONE,
                expected_code=304)


if __name__ == '__main__':
    SpecialCaseTrustAnchorRole().execute_scenario()
