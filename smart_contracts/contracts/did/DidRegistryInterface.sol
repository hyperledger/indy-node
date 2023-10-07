// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidDocument, DidDocumentStorage } from "./DidTypes.sol";

interface DidRegistryInterface {
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
     */
    function createDid(DidDocument calldata document) external;

    /**
     * Updates an existing DID
     * @param document The updated DID Document
     */
    function updateDid(DidDocument calldata document) external;

    /**
     * Deactivates a DID
     * @param id The DID to be deactivated
     */
    function deactivateDid(string calldata id) external;

    /**
     * @dev Function to resolve DID Document for the given DID
     * @param id The DID to be resolved
     */
    function resolveDid(string calldata id) external returns (DidDocumentStorage memory didDocumentStorage);
}
