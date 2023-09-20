// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface DidRegistryInterface {
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
     * Creates a new DID
     * @param document The new DID Document
     * @param signatures An array of DID Document signatures
     */
    function createDid(DidDocument calldata document, Signature[] calldata signatures) external;

    /**
     * Updates an existing DID
     * @param document The updated DID Document
     * @param signatures An array of DID Document signatures
     */
    function updateDid(DidDocument calldata document, Signature[] calldata signatures) external;

    /**
     * Deactivates a DID
     * @param id The DID to be deactivated
     * @param signatures An array of DID Document signatures
     */
    function deactivateDid(string calldata id, Signature[] calldata signatures) external;

    /**
     * @dev Function to resolve DID Document for the given DID
     * @param id The DID to be resolved
     */
    function resolve(string calldata id) external returns (DidDocument memory didDocument);
}
