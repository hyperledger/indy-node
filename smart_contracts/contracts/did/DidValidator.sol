// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { AuthenticationKeyNotFound, AuthenticationKeyRequired, IncorrectDid } from "./DidErrors.sol";
import { IncorrectDid } from "./DidErrors.sol";
import { DidRegex } from "./DidRegex.sol";
import { DidDocument, VerificationMethod } from "./DidTypes.sol";

using { toSlice } for string;

library DidValidator {
    /**
     * @dev Validates the DID syntax
     */
    function validateDid(string memory did) public pure {
        if (!DidRegex.matches(did)) revert IncorrectDid(did);
    }

    /**
     * @dev Validates verification keys
     */
    function validateVerificationKey(DidDocument memory didDocument) public pure {
        if (didDocument.authentication.length == 0) revert AuthenticationKeyRequired(didDocument.id);

        for (uint256 i = 0; i < didDocument.authentication.length; i++) {
            if (!didDocument.authentication[i].verificationMethod.id.toSlice().isEmpty()) {
                continue;
            }

            if (!_contains(didDocument.verificationMethod, didDocument.authentication[i].id)) {
                revert AuthenticationKeyNotFound(didDocument.authentication[i].id);
            }
        }
    }

    function _contains(VerificationMethod[] memory methods, string memory methodId) private pure returns (bool) {
        StrSlice methodIdSlice = methodId.toSlice();

        for (uint256 i; i < methods.length; i++) {
            if (methods[i].id.toSlice().eq(methodIdSlice)) {
                return true;
            }
        }

        return false;
    }
}
