from indy_common.types import SafeRequest


def test_validate_get_revoc_reg_entry(build_get_revoc_reg_entry):
    req = build_get_revoc_reg_entry
    SafeRequest(**req)
