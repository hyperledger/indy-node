import pytest

from indy_node.server.plugin.agent_authz.authz_checker import AgentAuthzChecker


def test_check_bad_params_to_auth():
    with pytest.raises(ValueError):
        AgentAuthzChecker(-3)
    with pytest.raises(ValueError):
        AgentAuthzChecker(-2.5)
    with pytest.raises(ValueError):
        AgentAuthzChecker(8.5)
    AgentAuthzChecker(8)
    AgentAuthzChecker(5)


def test_check_PROVE_auth():
    for i in [2, 6]:
        checker = AgentAuthzChecker(i)
        assert checker.has_prove_auth
        assert not checker.has_no_auth

    for i in [4, 12]:
        checker = AgentAuthzChecker(i)
        assert not checker.has_prove_auth
        assert not checker.has_no_auth


def test_check_PROVE_GRANT_auth():
    for i in [4, 12]:
        checker = AgentAuthzChecker(i)
        assert checker.has_prove_grant_auth
        assert not checker.has_no_auth

    for i in [2, 8, 10]:
        checker = AgentAuthzChecker(i)
        assert not checker.has_prove_grant_auth
        assert not checker.has_no_auth


def test_check_PROVE_REVOKE_auth():
    for i in [8, 10, 12, 14, 15]:
        checker = AgentAuthzChecker(i)
        assert checker.has_prove_revoke_auth
        assert not checker.has_no_auth

    for i in [2, 16]:
        checker = AgentAuthzChecker(i)
        assert not checker.has_prove_revoke_auth
        assert not checker.has_no_auth


def test_check_ADMIN_auth():
    for i in [1, 3, 5, 13, 15]:
        checker = AgentAuthzChecker(i)
        assert checker.has_admin_auth
        assert checker.has_prove_auth
        assert checker.has_prove_grant_auth
        assert checker.has_prove_revoke_auth
        assert not checker.has_no_auth


def test_check_no_auth():
    checker = AgentAuthzChecker(0)
    assert checker.has_no_auth
    assert not checker.has_admin_auth
    assert not checker.has_prove_auth
    assert not checker.has_prove_grant_auth
    assert not checker.has_prove_revoke_auth


def test_check_can_authorize_for():
    admin = AgentAuthzChecker(1)
    assert admin.can_authorize_for(1)
    assert admin.can_authorize_for(2)
    assert admin.can_authorize_for(4)
    assert admin.can_authorize_for(8)

    prover = AgentAuthzChecker(2)
    assert not prover.can_authorize_for(1)
    assert not prover.can_authorize_for(2)
    assert not prover.can_authorize_for(4)
    assert not prover.can_authorize_for(8)

    granter = AgentAuthzChecker(4)
    assert not granter.can_authorize_for(1)
    assert granter.can_authorize_for(2)
    assert not granter.can_authorize_for(4)
    assert not granter.can_authorize_for(8)

    revoker = AgentAuthzChecker(8)
    assert not revoker.can_authorize_for(1)
    assert not revoker.can_authorize_for(2)
    assert not revoker.can_authorize_for(4)
    assert not revoker.can_authorize_for(8)
