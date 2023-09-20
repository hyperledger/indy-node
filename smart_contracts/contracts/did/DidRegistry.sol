// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { DidRegistryInterface } from "./DidRegistryInterface.sol";

using { toSlice } for string;

contract DidRegistry is DidRegistryInterface {
    string private constant DELIMITER = ":";
    string private constant DID_PREFIX = "did";
    string private constant INDY_DID_METHOD = "indy";
    string private constant INDY_2_DID_METHOD = "indy2";
    string private constant SOV_DID_METHOD = "sov";

    /**
     * @dev Mapping DID to its corresponding DID Document.
     */
    mapping(string => DidDocumentStorage) private dids;

    /**
     * Checks that DID already exists
     */
    modifier didExist(string memory did) {
        require(dids[did].metadata.created != 0, "DID not found");
        _;
    }

    /**
     * Checks that the DID has not yet been added
     */
    modifier didNotExist(string memory did) {
        require(dids[did].metadata.created == 0, "DID has already exist");
        _;
    }

    /**
     * Validated the DID syntax
     */
    modifier validDid(string memory did) {
        StrSlice didSlice = did.toSlice();
        StrSlice delimiterSlice = DELIMITER.toSlice();

        (, StrSlice schema, StrSlice rest) = didSlice.splitOnce(delimiterSlice);
        require(schema.eq(DID_PREFIX.toSlice()), "Incorrect DID schema");

        (, StrSlice didMethod, ) = rest.splitOnce(delimiterSlice);
        require(
            didMethod.eq(INDY_DID_METHOD.toSlice())
                || didMethod.eq(INDY_2_DID_METHOD.toSlice())
                || didMethod.eq(SOV_DID_METHOD.toSlice()),
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
            if (!didDocument.authentication[i].verificationMethod.id.toSlice().isEmpty()) {
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

    /**
     * @dev Function to resolve DID Document for the given DID
     * @param id The DID to be resolved
     */
    function resolve(
        string calldata id
    ) public didExist(id) view virtual returns (DidDocumentStorage memory didDocumentStorage) {
        return dids[id];
    }

    function contains(VerificationMethod[] memory methods, string memory methodId) private pure returns (bool) {
         StrSlice methodIdSlice = methodId.toSlice();

        for (uint i; i < methods.length; i++) {
            if (methods[i].id.toSlice().eq(methodIdSlice)) {
                return true;
            }
        }

        return false;
    }
}
