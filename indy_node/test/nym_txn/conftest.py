import pytest


@pytest.fixture(scope="function", params=[False, True])
def with_verkey(request):
    return request.param
