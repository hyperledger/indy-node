// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidNotFound } from "../did/DidErrors.sol";
import { DidRegistryInterface } from "../did/DidRegistry.sol";
import { DidDocumentStorage } from "../did/DidTypes.sol";
import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { Errors } from "../utils/Errors.sol";

import { IssuerHasBeenDeactivated, IssuerNotFound, SchemaAlreadyExist, SchemaNotFound, SenderIsNotIssuerDidOwner } from "./ClErrors.sol";
import { CLRegistry } from "./CLRegistry.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaWithMetadata } from "./SchemaTypes.sol";
import { SchemaValidator } from "./SchemaValidator.sol";
import { toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";

using SchemaValidator for Schema;
using { toSlice } for string;

// TODO: Think of adding `DidUniversalResolver` contract so that adding a support for new DID method (like `did:ethr`)
//  will require updating version of only `DIDUniversalResolver` contract only.
//  CLRegistry registry use `DIDUniversalResolver` to get DID Record and validate as needed
//interface DIDUniversalRegistryResolver {
//    function resolveDid()
//}

contract CLRegistry {
    /**
     * @dev Reference to the contract that manages DIDs
     */
    DidRegistryInterface internal _didRegistry; // did:indy2

    /**
     * Checks that the Issuer DID exist, controlled by sender, and active
     */
    modifier _validIssuer(string memory id) {
        try _didRegistry.resolveDid(id) returns (DidDocumentStorage memory didDocumentStorage) {
            if (msg.sender != didDocumentStorage.metadata.creator)
                revert SenderIsNotIssuerDidOwner(msg.sender, didDocumentStorage.metadata.creator);
            if (didDocumentStorage.metadata.deactivated) revert IssuerHasBeenDeactivated(id);
            _;
        } catch (bytes memory reason) {
            if (Errors.equals(reason, DidNotFound.selector)) {
                revert IssuerNotFound(id);
            }

            Errors.rethrow(reason);
        }
    }
}
