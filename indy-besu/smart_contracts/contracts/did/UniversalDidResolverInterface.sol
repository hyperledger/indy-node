// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidDocument, DidMetadata } from "./DidTypes.sol";

/**
 * @title The interface that defines functions to resolve DID from various DID registries
 */
interface UniversalDidResolverInterface {
    /**
     * @dev Function to resolve DID Document for the given DID.
     *
     * Restrictions:
     * - DID must exist; otherwise, will revert with a `DidNotFound` error.
     *
     * @param id The DID to be resolved.
     * @return document The resolved DID document associated with provided DID.
     */
    function resolveDocument(string memory id) external view returns (DidDocument memory document);

    /**
     * @dev Function to resolve DID Metadata for the given DID.
     *
     * Restrictions:
     * - DID must exist; otherwise, will revert with a `DidNotFound` error.
     *
     * @param id The DID to be resolved.
     * @return metadata The resolved DID metadata associated with provided DID.
     */
    function resolveMetadata(string memory id) external view returns (DidMetadata memory metadata);
}
