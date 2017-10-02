import pytest


@pytest.mark.skip("SOV-566. Not yet implemented")
def testUnsignedRequest():
    """
    Ensure an unsigned request is not allowed.
    """
    raise NotImplementedError


@pytest.mark.skip("SOV-566. Not yet implemented")
def testRequestSignedByUnknownIdentifier():
    """
    Ensure a request signed by an unknown party is not allowed.
    """
    raise NotImplementedError


@pytest.mark.skip("SOV-566. Not yet implemented")
def testRequestSignedByKnownIdentifier():
    """
    Ensure a properly signed request is allowed.
    """
    raise NotImplementedError
