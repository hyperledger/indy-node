// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract DidRegistry {
    struct DidDocumentStorage {
        DidDocument document;
        DidMetadata metadata;
    }

    struct DidMetadata {
        uint256 created;
        uint256 updated;
        bool deactivated;
    }

    struct DidDocument {
        string[] context;
        string id;
        string[] controller;
        VerificationMethod[] verificationMethod;
        VerificationRelationship[] authentication;
        VerificationRelationship[] assertionMethod;
        VerificationRelationship[] capabilityInvocation;
        VerificationRelationship[] capabilityDelegation;
        VerificationRelationship[] keyAgreement;
        Service[] service;
        string[] alsoKnownAs;
    }

    struct VerificationMethod {
        string id;
        string verificationMethodType;
        string controller;
        string publicKeyJwk;
        string publicKeyMultibase;
    }

    struct VerificationRelationship {
        string id;
        VerificationMethod verificationMethod;
    }

    struct Service {
        string id;
        string serviceType;
        string[] serviceEndpoint;
        string[] accept;
        string[] routingKeys;
    }

    struct Signature {
        string id;
        string value;
    }

    mapping(string => DidDocumentStorage) public dids;

    event DIDCreated(string did);
    event DIDUpdated(string did);
    event DIDDeactivated(string did);

    modifier didExist(string memory did) {
        require(dids[did].metadata.created != 0, "DID not found");
        _;
    }

    modifier didNotExist(string memory did) {
        require(dids[did].metadata.created == 0, "DID has already exist");
        _;
    }

    modifier didIsActive(string memory did) {
        require(!dids[did].metadata.deactivated, "DID has been deactivated");
        _;
    }

    function createDid(
        DidDocument calldata document,
        Signature[] calldata signatures
    ) public didNotExist(document.id) {
        dids[document.id].document = document;
        dids[document.id].metadata.created = block.timestamp;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDCreated(document.id);
    }

    function updateDidDocument(
        DidDocument calldata document,
        Signature[] calldata signatures
    ) public didExist(document.id) didIsActive(document.id) {
        dids[document.id].document = document;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDUpdated(document.id);
    }

    function deactivateDid(
        string calldata id,
        Signature[] calldata signatures
    ) public didExist(id) didIsActive(id) {
        dids[id].metadata.deactivated = true;

        emit DIDDeactivated(id);
    }

    function isEquals(
        string memory string1,
        string memory string2
    ) private pure returns (bool) {
        return keccak256(bytes(string1)) == keccak256(bytes(string2));
    }

    function isEmpty(string memory _string) private pure returns (bool) {
        return bytes(_string).length == 0;
    }
}
