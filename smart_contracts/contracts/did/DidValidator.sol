// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { DidDocument, VerificationMethod } from "./DidTypes.sol";

using { toSlice } for string;

library DidValidator {
    string private constant DELIMITER = ":";
    string private constant DID_PREFIX = "did";
    string private constant INDY_DID_METHOD = "indy";
    string private constant INDY_2_DID_METHOD = "indy2";
    string private constant SOV_DID_METHOD = "sov";

    /**
     * @dev Validates the DID syntax
     */
    function validateDid(string memory did) public pure {
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