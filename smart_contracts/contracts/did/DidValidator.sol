// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { DidRegex } from "./DidRegex.sol";
import { DidDocument, VerificationMethod } from "./DidTypes.sol";

using { toSlice } for string;

library DidValidator {
    /**
     * @dev Validates the DID syntax
     */
    function validateDid(string memory did) public pure {
        require(DidRegex.matches(did), "Incorrect DID");
    }

    /**
     * @dev Validates verification keys
     */
    function validateVerificationKey(DidDocument memory didDocument) public pure {
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
