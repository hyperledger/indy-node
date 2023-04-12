def test_get_fees(get_fees_request, get_fees_handler):
    """
    StaticValidation of a get fees request does nothing.
    """
    get_fees_handler.static_validation(get_fees_request)
