// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { strings } from "./utils/string.sol";

contract DidRegistry {
    using strings for *;

    /**
     * @dev DidDocumentStorage holds the DID Document and its associated metadata
     */
    struct DidDocumentStorage {
        DidDocument document;
        DidMetadata metadata;
    }

    /**
     * @dev VerificationRelationship links a DID to a verification method
     */
    struct DidMetadata {
        uint256 created;
        uint256 updated;
        bool deactivated;
    }

    /**
     * @dev DidDocument represent the main DID Document structure.
     */
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

    /**
     * @dev VerificationMethod are used to define how to authenticate/authorise interactions with a DID subject or delegates.
     */
    struct VerificationMethod {
        string id;
        string verificationMethodType;
        string controller;
        string publicKeyJwk;
        string publicKeyMultibase;
    }

    /**
     * @dev VerificationRelationship links a DID to a verification method.
     */
    struct VerificationRelationship {
        string id;
        VerificationMethod verificationMethod;
    }

    /**
     * @dev Service describes a service endpoint related to the DID.
     */
    struct Service {
        string id;
        string serviceType;
        string[] serviceEndpoint;
        string[] accept;
        string[] routingKeys;
    }

    /**
     * @dev Signature describes DID Document signature
     */
    struct Signature {
        string id;
        string value;
    }

    /**
     * @dev Event that is sent when a DID Document is created
     */
    event DIDCreated(string did);

    /**
     * @dev Event that is sent when a DID Document is updated
     */
    event DIDUpdated(string did);

    /**
     * @dev Event that is sent when a DID Document is deactivated
     */
    event DIDDeactivated(string did);

    /**
     * @dev Mapping DID to its corresponfing DID Document.
     */
    mapping(string => DidDocumentStorage) public dids;

    /**
     * Checks that DID already exists
     */
    modifier didExist(string memory did) {
        require(dids[did].metadata.created != 0, "DID not found");
        _;
    }

    /**
     * Сhecks that the DID has not yet been added
     */
    modifier didNotExist(string memory did) {
        require(dids[did].metadata.created == 0, "DID has already exist");
        _;
    }

    /**
     * Validated the DID syntax
     */
    modifier validDid(string memory did) {
        strings.slice memory didSlice = did.toSlice();
        strings.slice memory delimiter = ':'.toSlice();

        strings.slice memory schema = didSlice.split(delimiter);
        
        require(schema.equals("did".toSlice()), "Incorrect DID schema");

        strings.slice memory didMethod = didSlice.split(delimiter);

        require(
            didMethod.equals("indy2".toSlice()) 
                || didMethod.equals("indy".toSlice()) 
                || didMethod.equals("sov".toSlice()), 
            "Unsupported DID method"
        );
        _;
    }

    /**
     * Validated verification keys
     */
    modifier validVerificationKey(DidDocument memory didDocument) {
        require(didDocument.authentication.length != 0, "Authentication key is required");
        
         for (uint i = 0; i < didDocument.authentication.length; i++) {
            if (!didDocument.authentication[i].verificationMethod.id.toSlice().empty()) {
                continue;
            }

            require (
                contains(
                    didDocument.verificationMethod, didDocument.authentication[i].id), 
                    string.concat("Authentication key for ID: ", didDocument.authentication[i].id, " is not found"
                )
            );
         }
        _;
    }


    /**
     * Сhecks that the DID has not been deactivated
     */
    modifier didIsActive(string memory did) {
        require(!dids[did].metadata.deactivated, "DID has been deactivated");
        _;
    }

    /**
     * Creates a new DID
     * @param document The new DID Document
     * @param signatures An array of DID Document signatures
     */
    function createDid(
        DidDocument calldata document,
        Signature[] calldata signatures
    ) public didNotExist(document.id) validDid(document.id) validVerificationKey(document) {
        dids[document.id].document = document;
        dids[document.id].metadata.created = block.timestamp;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDCreated(document.id);
    }

    /**
     * Updates an existing DID
     * @param document The updated DID Document
     * @param signatures An array of DID Document signatures
     */
    function updateDid(
        DidDocument calldata document,
        Signature[] calldata signatures
    ) public didExist(document.id) didIsActive(document.id) validVerificationKey(document) {
        dids[document.id].document = document;
        dids[document.id].metadata.updated = block.timestamp;

        emit DIDUpdated(document.id);
    }

    /**
     * Deactivates a DID
     * @param id The DID to be deactivated
     * @param signatures An array of DID Document signatures
     */
    function deactivateDid(
        string calldata id,
        Signature[] calldata signatures
    ) public didExist(id) didIsActive(id) {
        dids[id].metadata.deactivated = true;

        emit DIDDeactivated(id);
    }

    function contains(VerificationMethod[] memory methods, string memory methodId) private pure returns (bool) {
         strings.slice memory methodIdSlice = methodId.toSlice();

        for (uint i; i < methods.length; i++) {
            if (methods[i].id.toSlice().equals(methodIdSlice)) {
                return true;
            }
        }

        return false;
    }
}
