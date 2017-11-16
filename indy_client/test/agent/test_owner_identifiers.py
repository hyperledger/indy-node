import pytest


@pytest.mark.skip("SOV-565. Not yet implemented")
def test_add_identifier():
    """
    Add an owner identifier.
    Ensure the appropriate values are set for the associated synced key.
    """
    raise NotImplementedError


@pytest.mark.skip("SOV-565. Not yet implemented")
def test_add_second_identifier():
    """
    Add another owner identifier.
    Ensure agent.ownerIdentifiers is set up properly.
    """
    raise NotImplementedError


@pytest.mark.skip("SOV-565. Not yet implemented")
def test_sync_identifier_keys():
    """
    Connect to the indy network and ensure we have the latest keys for all of
    the owner's identifiers.
    """
    raise NotImplementedError
