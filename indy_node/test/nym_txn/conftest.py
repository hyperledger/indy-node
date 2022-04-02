import json

import pytest


@pytest.fixture(scope="function", params=[False, True])
def with_verkey(request):
    return request.param


@pytest.fixture
def diddoc_content():
    yield {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://identity.foundation/didcomm-messaging/service-endpoint/v1",
        ],
        "serviceEndpoint": [
            {
                "id": "did:indy:sovrin:123456#didcomm",
                "type": "didcomm-messaging",
                "serviceEndpoint": "https://example.com",
                "recipientKeys": ["#verkey"],
                "routingKeys": [],
            }
        ],
    }


@pytest.fixture
def diddoc_content_json(diddoc_content):
    yield json.dumps(diddoc_content)
