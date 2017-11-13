#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import pytest
from indy import IndyError
from indy.error import ErrorCode
from pytest import raises

from indy_acceptance.test.constants import TRUSTEE_CODE, STEWARD_CODE,\
    TGB_CODE, TRUST_ANCHOR_CODE, NO_ROLE_CODE


@pytest.mark.skip(reason='IS-347')
@pytest.mark.asyncio
async def test_remove_add_roles(client):

    # GENERATE DIDS AND VERKEYS

    test_trustee1_did, test_trustee1_verkey = \
        await client.new_did(seed='TestTrustee100000000000000000000')
    test_trustee2_did, test_trustee2_verkey = \
        await client.new_did(seed='TestTrustee200000000000000000000')
    test_steward1_did, test_steward1_verkey = \
        await client.new_did(seed='TestSteward100000000000000000000')
    test_steward2_did, test_steward2_verkey = \
        await client.new_did(seed='TestSteward200000000000000000000')
    test_steward3_did, test_steward3_verkey = \
        await client.new_did(seed='TestSteward300000000000000000000')
    test_tgb1_did, test_tgb1_verkey = \
        await client.new_did(seed='TestTGB1000000000000000000000000')
    test_trust_anchor1_did, test_trust_anchor1_verkey = \
        await client.new_did(seed='TestTrustAnchor10000000000000000')
    test_trust_anchor2_did, test_trust_anchor2_verkey = \
        await client.new_did(seed='TestTrustAnchor20000000000000000')
    test_trust_anchor3_did, test_trust_anchor3_verkey = \
        await client.new_did(seed='TestTrustAnchor30000000000000000')
    random_user1_did, random_user1_verkey = \
        await client.new_did(seed='RandomUser1000000000000000000000')
    random_user2_did, random_user2_verkey = \
        await client.new_did(seed='RandomUser2000000000000000000000')
    random_user3_did, random_user3_verkey = \
        await client.new_did(seed='RandomUser3000000000000000000000')
    random_user4_did, random_user4_verkey = \
        await client.new_did(seed='RandomUser4000000000000000000000')
    random_user5_did, random_user5_verkey = \
        await client.new_did(seed='RandomUser5000000000000000000000')
    random_user6_did, random_user6_verkey = \
        await client.new_did(seed='RandomUser6000000000000000000000')

    # TEST ROLE PERMISSIONS

    # ==========================================================================
    await client.new_did(seed='000000000000000000000000Trustee1')

    await client.send_nym(dest=test_trustee1_did,
                          verkey=test_trustee1_verkey,
                          role='TRUSTEE')
    test_trustee1_nym = await client.send_get_nym(test_trustee1_did)
    assert test_trustee1_nym['dest'] == test_trustee1_did
    assert test_trustee1_nym['verkey'] == test_trustee1_verkey
    assert test_trustee1_nym['role'] == TRUSTEE_CODE

    # ==========================================================================
    await client.use_did(test_trustee1_did)

    await client.send_nym(dest=test_steward1_did,
                          verkey=test_steward1_verkey,
                          role='STEWARD')
    test_steward1_nym = await client.send_get_nym(test_steward1_did)
    assert test_steward1_nym['dest'] == test_steward1_did
    assert test_steward1_nym['verkey'] == test_steward1_verkey
    assert test_steward1_nym['role'] == STEWARD_CODE

    await client.send_nym(dest=random_user3_did,
                          verkey=random_user3_verkey)
    random_user3_nym = await client.send_get_nym(random_user3_did)
    assert random_user3_nym['dest'] == random_user3_did
    assert random_user3_nym['verkey'] == random_user3_verkey
    assert random_user3_nym['role'] == NO_ROLE_CODE

    await client.send_nym(dest=test_tgb1_did,
                          verkey=test_tgb1_verkey,
                          role='TGB')
    test_tgb1_nym = await client.send_get_nym(test_tgb1_did)
    assert test_tgb1_nym['dest'] == test_tgb1_did
    assert test_tgb1_nym['verkey'] == test_tgb1_verkey
    assert test_tgb1_nym['role'] == TGB_CODE

    # ==========================================================================
    await client.use_did(test_steward1_did)

    await client.send_nym(dest=test_trust_anchor1_did,
                          verkey=test_trust_anchor1_verkey,
                          role='TRUST_ANCHOR')
    test_trust_anchor1_nym = await client.send_get_nym(test_trust_anchor1_did)
    assert test_trust_anchor1_nym['dest'] == test_trust_anchor1_did
    assert test_trust_anchor1_nym['verkey'] == test_trust_anchor1_verkey
    assert test_trust_anchor1_nym['role'] == TRUST_ANCHOR_CODE

    await client.send_nym(dest=random_user4_did,
                          verkey=random_user4_verkey)
    random_user4_nym = await client.send_get_nym(random_user4_did)
    assert random_user4_nym['dest'] == random_user4_did
    assert random_user4_nym['verkey'] == random_user4_verkey
    assert random_user4_nym['role'] == NO_ROLE_CODE

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_steward2_did,
                              verkey=test_steward2_verkey,
                              role='STEWARD')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trustee2_did,
                              verkey=test_trustee2_verkey,
                              role='TRUSTEE')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # ==========================================================================
    await client.use_did(test_trust_anchor1_did)

    await client.send_nym(dest=random_user1_did,
                          verkey=random_user1_verkey)
    random_user1_nym = await client.send_get_nym(random_user1_did)
    assert random_user1_nym['dest'] == random_user1_did
    assert random_user1_nym['verkey'] == random_user1_verkey
    assert random_user1_nym['role'] == NO_ROLE_CODE

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trust_anchor2_did,
                              verkey=test_trust_anchor2_verkey,
                              role='TRUST_ANCHOR')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # TEST REMOVING ROLES

    # ==========================================================================
    await client.new_did(seed='000000000000000000000000Trustee1')

    await client.send_nym(dest=test_trustee1_did,
                          role='')
    await client.send_nym(dest=test_steward1_did,
                          role='')
    await client.send_nym(dest=test_tgb1_did,
                          role='')
    await client.send_nym(dest=test_trust_anchor1_did,
                          role='')

    # ==========================================================================
    await client.use_did(test_trustee1_did)

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trustee2_did,
                              verkey=test_trustee2_verkey,
                              role='TRUSTEE')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_steward2_did,
                              verkey=test_steward2_verkey,
                              role='STEWARD')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # ==========================================================================
    await client.use_did(test_steward1_did)

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trust_anchor2_did,
                              verkey=test_trust_anchor2_verkey,
                              role='TRUST_ANCHOR')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # TEST ADDING ROLES

    # ==========================================================================
    await client.new_did(seed='000000000000000000000000Trustee1')

    await client.send_nym(dest=test_trustee1_did,
                          role='TRUSTEE')

    # ==========================================================================
    await client.use_did(test_trustee1_did)

    await client.send_nym(dest=test_steward1_did,
                          role='STEWARD')
    await client.send_nym(dest=test_tgb1_did,
                          role='TGB')

    # ==========================================================================
    await client.use_did(test_steward1_did)

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trust_anchor1_did,
                              role='TRUST_ANCHOR')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_trustee1_did,
                              role='')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # ==========================================================================
    await client.use_did(test_trustee1_did)

    await client.send_nym(dest=test_steward3_did,
                          verkey=test_steward3_verkey,
                          role='STEWARD')

    await client.send_nym(dest=test_steward2_did,
                          verkey=test_steward2_verkey,
                          role='STEWARD')

    # ==========================================================================
    await client.use_did(test_steward1_did)

    with raises(IndyError) as exInfo:
        await client.send_nym(dest=test_steward2_did,
                              role='')
    assert exInfo.value.error_code == ErrorCode.LedgerInvalidTransaction

    # ==========================================================================
    await client.use_did(test_steward2_did)

    await client.send_nym(dest=test_trust_anchor3_did,
                          verkey=test_trust_anchor3_verkey,
                          role='TRUST_ANCHOR')
