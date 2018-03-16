# TODO: Code to create a new policy data object from authorisation integer and expose methods to check specific authorisations.
from ledger.util import has_nth_bit_set


class AgentAuthzChecker:
    """
    ```
    0 None (revoked)
    1 ADMIN (all)
    2 PROVE
    4 PROVE_GRANT
    8 PROVE_REVOKE
    16 "Reserved for future"
    32 "Reserved for future"
    64  ...
       ...
    ```
    """
    def __init__(self, authz_int: int):
        if not isinstance(authz_int, int) or authz_int < 0:
            raise ValueError('should be a positive integer and not '
                             '{}'.format(authz_int))
        self.authz_value = authz_int

    @property
    def has_no_auth(self) -> bool:
        return self.authz_value == 0

    @property
    def has_admin_auth(self) -> bool:
        return has_nth_bit_set(self.authz_value, 0)

    @property
    def has_prove_auth(self) -> bool:
        return self.has_admin_auth or has_nth_bit_set(self.authz_value, 1)

    @property
    def has_prove_grant_auth(self) -> bool:
        return self.has_admin_auth or has_nth_bit_set(self.authz_value, 2)

    @property
    def has_prove_revoke_auth(self) -> bool:
        return self.has_admin_auth or has_nth_bit_set(self.authz_value, 3)

    def can_authorize_for(self, auth):
        auth = AgentAuthzChecker(auth)

        if auth.has_prove_auth and not self.has_prove_grant_auth:
            return False
        if auth.has_prove_grant_auth and not self.has_admin_auth:
            return False
        if auth.has_prove_revoke_auth and not self.has_admin_auth:
            return False
        if auth.has_admin_auth and not self.has_admin_auth:
            return False

        return True
