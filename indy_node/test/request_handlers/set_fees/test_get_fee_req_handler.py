def test_get_fee_valid_alias(get_fee_request, get_fee_handler):
    """
    StaticValidation of a get fee request with all of the whitelisted txn
    types.
    """
    result = get_fee_handler.static_validation(get_fee_request)
    assert result is None
