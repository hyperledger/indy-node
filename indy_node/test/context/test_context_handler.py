
import pytest
from indy_node.server.request_handlers.domain_req_handlers.context_handler import ContextHandler
from plenum.common.request import Request


def test_validate_context_fail_on_empty():
    with pytest.raises(Exception) as e:
        ContextHandler._validate_context({})
    assert "Context missing '@context' property" in str(e.value)


def test_validate_context_fail_no_context_property():
    input_dict = {
        "name": "Thing"
    }
    with pytest.raises(Exception) as e:
        ContextHandler._validate_context(input_dict)
    assert "Context missing '@context' property" in str(e.value)


@pytest.mark.skip("Until we find a string that fails the regex, or improve the test, this should be skipped")
def test_validate_context_fail_bad_uri():
    input_dict = {
        "@context": "2http:/..@#$"
    }
    with pytest.raises(Exception) as e:
        ContextHandler._validate_context(input_dict)
    assert "fail" in str(e.value)


def test_validate_context_fail_context_not_uri_or_array_or_object():
    input_dict = {
        "@context": 52
    }
    with pytest.raises(Exception) as e:
        ContextHandler._validate_context(input_dict)
    assert "'@context' value must be url, array, or object" in str(e.value)


def test_validate_context_pass_value_is_dict():
    input_dict = {
        "@context": {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        }
    }
    ContextHandler._validate_context(input_dict)


def test_validate_context_pass_value_is_list():
    input_dict = {
        "@context": [
            {
                "favoriteColor": "https://example.com/vocab#favoriteColor"
            },
            "https://www.w3.org/ns/odrl.jsonld"
        ]
    }
    ContextHandler._validate_context(input_dict)


def test_validate_context_pass_context_w3c_example_15():
    input_dict = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    ContextHandler._validate_context(input_dict)


def test_static_validation_pass_valid_transaction():
    operation = {
        "data": {
            "name": "TestContext",
            "version": 1,
            "context_array": w3c_base
        },
        "type": "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_validate_context_pass_context_w3c_base():
    # pasted directly out of the reference file, without any format changes
    # change true to True to correct for python
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    ContextHandler._validate_context(w3c_base)


def test_static_validation_pass_valid_transaction():
    operation = {
        "data": {
            "name": "TestContext",
            "version": 1,
            "context": w3c_base
        },
        "type": "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_validate_context_pass_context_w3c_examples_v1():
    # test for https://www.w3.org/2018/credentials/examples/v1
    ContextHandler._validate_context(w3c_example_v1)


w3c_base = {
    "@context": {
        "@version": 1.1,
        "@protected": True,
        "id": "@id",
        "type": "@type",
        "VerifiableCredential": {
            "@id": "https://www.w3.org/2018/credentials#VerifiableCredential",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "id": "@id",
                "type": "@type",
                "cred": "https://www.w3.org/2018/credentials#",
                "sec": "https://w3id.org/security#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "credentialSchema": {
                    "@id": "cred:credentialSchema",
                    "@type": "@id",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "cred": "https://www.w3.org/2018/credentials#",
                        "JsonSchemaValidator2018": "cred:JsonSchemaValidator2018"
                    }
                },
                "credentialStatus": {"@id": "cred:credentialStatus", "@type": "@id"},
                "credentialSubject": {"@id": "cred:credentialSubject", "@type": "@id"},
                "evidence": {"@id": "cred:evidence", "@type": "@id"},
                "expirationDate": {"@id": "cred:expirationDate", "@type": "xsd:dateTime"},
                "holder": {"@id": "cred:holder", "@type": "@id"},
                "issued": {"@id": "cred:issued", "@type": "xsd:dateTime"},
                "issuer": {"@id": "cred:issuer", "@type": "@id"},
                "issuanceDate": {"@id": "cred:issuanceDate", "@type": "xsd:dateTime"},
                "proof": {"@id": "sec:proof", "@type": "@id", "@container": "@graph"},
                "refreshService": {
                    "@id": "cred:refreshService",
                    "@type": "@id",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "cred": "https://www.w3.org/2018/credentials#",
                        "ManualRefreshService2018": "cred:ManualRefreshService2018"
                    }
                },
                "termsOfUse": {"@id": "cred:termsOfUse", "@type": "@id"},
                "validFrom": {"@id": "cred:validFrom", "@type": "xsd:dateTime"},
                "validUntil": {"@id": "cred:validUntil", "@type": "xsd:dateTime"}
            }
        },
        "VerifiablePresentation": {
            "@id": "https://www.w3.org/2018/credentials#VerifiablePresentation",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "id": "@id",
                "type": "@type",
                "cred": "https://www.w3.org/2018/credentials#",
                "sec": "https://w3id.org/security#",
                "holder": {"@id": "cred:holder", "@type": "@id"},
                "proof": {"@id": "sec:proof", "@type": "@id", "@container": "@graph"},
                "verifiableCredential": {"@id": "cred:verifiableCredential", "@type": "@id", "@container": "@graph"}
            }
        },
        "EcdsaSecp256k1Signature2019": {
            "@id": "https://w3id.org/security#EcdsaSecp256k1Signature2019",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "id": "@id",
                "type": "@type",
                "sec": "https://w3id.org/security#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "challenge": "sec:challenge",
                "created": {"@id": "http://purl.org/dc/terms/created", "@type": "xsd:dateTime"},
                "domain": "sec:domain",
                "expires": {"@id": "sec:expiration", "@type": "xsd:dateTime"},
                "jws": "sec:jws",
                "nonce": "sec:nonce",
                "proofPurpose": {
                    "@id": "sec:proofPurpose",
                    "@type": "@vocab",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "sec": "https://w3id.org/security#",
                        "assertionMethod": {"@id": "sec:assertionMethod", "@type": "@id", "@container": "@set"},
                        "authentication": {"@id": "sec:authenticationMethod", "@type": "@id", "@container": "@set"}
                    }
                },
                "proofValue": "sec:proofValue",
                "verificationMethod": {"@id": "sec:verificationMethod", "@type": "@id"}
            }
        },
        "EcdsaSecp256r1Signature2019": {
            "@id": "https://w3id.org/security#EcdsaSecp256r1Signature2019",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "id": "@id",
                "type": "@type",
                "sec": "https://w3id.org/security#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "challenge": "sec:challenge",
                "created": {"@id": "http://purl.org/dc/terms/created", "@type": "xsd:dateTime"},
                "domain": "sec:domain",
                "expires": {"@id": "sec:expiration", "@type": "xsd:dateTime"},
                "jws": "sec:jws",
                "nonce": "sec:nonce",
                "proofPurpose": {
                    "@id": "sec:proofPurpose",
                    "@type": "@vocab",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "sec": "https://w3id.org/security#",
                        "assertionMethod": {"@id": "sec:assertionMethod", "@type": "@id", "@container": "@set"},
                        "authentication": {"@id": "sec:authenticationMethod", "@type": "@id", "@container": "@set"}
                    }
                },
                "proofValue": "sec:proofValue",
                "verificationMethod": {"@id": "sec:verificationMethod", "@type": "@id"}
            }
        },
        "Ed25519Signature2018": {
            "@id": "https://w3id.org/security#Ed25519Signature2018",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "id": "@id",
                "type": "@type",
                "sec": "https://w3id.org/security#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "challenge": "sec:challenge",
                "created": {"@id": "http://purl.org/dc/terms/created", "@type": "xsd:dateTime"},
                "domain": "sec:domain",
                "expires": {"@id": "sec:expiration", "@type": "xsd:dateTime"},
                "jws": "sec:jws",
                "nonce": "sec:nonce",
                "proofPurpose": {
                    "@id": "sec:proofPurpose",
                    "@type": "@vocab",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "sec": "https://w3id.org/security#",
                        "assertionMethod": {"@id": "sec:assertionMethod", "@type": "@id", "@container": "@set"},
                        "authentication": {"@id": "sec:authenticationMethod", "@type": "@id", "@container": "@set"}
                    }
                },
                "proofValue": "sec:proofValue",
                "verificationMethod": {"@id": "sec:verificationMethod", "@type": "@id"}
            }
        },
        "RsaSignature2018": {
            "@id": "https://w3id.org/security#RsaSignature2018",
            "@context": {
                "@version": 1.1,
                "@protected": True,
                "challenge": "sec:challenge",
                "created": {"@id": "http://purl.org/dc/terms/created", "@type": "xsd:dateTime"},
                "domain": "sec:domain",
                "expires": {"@id": "sec:expiration", "@type": "xsd:dateTime"},
                "jws": "sec:jws",
                "nonce": "sec:nonce",
                "proofPurpose": {
                    "@id": "sec:proofPurpose",
                    "@type": "@vocab",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "sec": "https://w3id.org/security#",
                        "assertionMethod": {"@id": "sec:assertionMethod", "@type": "@id", "@container": "@set"},
                        "authentication": {"@id": "sec:authenticationMethod", "@type": "@id", "@container": "@set"}
                    }
                },
                "proofValue": "sec:proofValue",
                "verificationMethod": {"@id": "sec:verificationMethod", "@type": "@id"}
            }
        },
        "proof": {"@id": "https://w3id.org/security#proof", "@type": "@id", "@container": "@graph"}
    }
}

w3c_example_v1 = {
    "@context": [
        {
            "@version": 1.1
        },
        "https://www.w3.org/ns/odrl.jsonld",
        {
            "ex": "https://example.org/examples#",
            "schema": "http://schema.org/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "3rdPartyCorrelation": "ex:3rdPartyCorrelation",
            "AllVerifiers": "ex:AllVerifiers",
            "Archival": "ex:Archival",
            "BachelorDegree": "ex:BachelorDegree",
            "Child": "ex:Child",
            "CLCredentialDefinition2019": "ex:CLCredentialDefinition2019",
            "CLSignature2019": "ex:CLSignature2019",
            "IssuerPolicy": "ex:IssuerPolicy",
            "HolderPolicy": "ex:HolderPolicy",
            "Mother": "ex:Mother",
            "RelationshipCredential": "ex:RelationshipCredential",
            "UniversityDegreeCredential": "ex:UniversityDegreeCredential",
            "ZkpExampleSchema2018": "ex:ZkpExampleSchema2018",
            "issuerData": "ex:issuerData",
            "attributes": "ex:attributes",
            "signature": "ex:signature",
            "signatureCorrectnessProof": "ex:signatureCorrectnessProof",
            "primaryProof": "ex:primaryProof",
            "nonRevocationProof": "ex:nonRevocationProof",
            "alumniOf": {"@id": "schema:alumniOf", "@type": "rdf:HTML"},
            "child": {"@id": "ex:child", "@type": "@id"},
            "degree": "ex:degree",
            "degreeType": "ex:degreeType",
            "degreeSchool": "ex:degreeSchool",
            "college": "ex:college",
            "name": {"@id": "schema:name", "@type": "rdf:HTML"},
            "givenName": "schema:givenName",
            "familyName": "schema:familyName",
            "parent": {"@id": "ex:parent", "@type": "@id"},
            "referenceId": "ex:referenceId",
            "documentPresence": "ex:documentPresence",
            "evidenceDocument": "ex:evidenceDocument",
            "spouse": "schema:spouse",
            "subjectPresence": "ex:subjectPresence",
            "verifier": {"@id": "ex:verifier", "@type": "@id"}
        }
    ]
}
