// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StringUtils } from "../utils/StringUtils.sol";
import { DidUtils, ParsedDid } from "../utils/DidUtils.sol";
import { AuthenticationKeyNotFound, AuthenticationKeyRequired, IncorrectDid } from "./DidErrors.sol";
import { IncorrectDid } from "./DidErrors.sol";
import { DidDocument, VerificationMethod } from "./DidTypes.sol";

using StringUtils for string;

library IndyDidValidator {
    /**
     * @dev Validates the DID syntax
     */
    function validateDid(string memory did) public view {
        ParsedDid memory parsedDid = DidUtils.parseDid(did);

        if (!DidUtils.isIndyMethod(parsedDid.method)) revert IncorrectDid(did);

        uint256 identifierLength = parsedDid.identifier.length();
        if (identifierLength != 21 && identifierLength != 22) revert IncorrectDid(parsedDid.identifier);
    }

    /**
     * @dev Validates verification keys
     */
    function validateVerificationKey(DidDocument memory didDocument) public pure {
        if (didDocument.authentication.length == 0) revert AuthenticationKeyRequired(didDocument.id);

        for (uint256 i = 0; i < didDocument.authentication.length; i++) {
            if (!didDocument.authentication[i].verificationMethod.id.isEmpty()) {
                continue;
            }

            if (!_contains(didDocument.verificationMethod, didDocument.authentication[i].id)) {
                revert AuthenticationKeyNotFound(didDocument.authentication[i].id);
            }
        }
    }

    function _contains(VerificationMethod[] memory methods, string memory methodId) private pure returns (bool) {
        for (uint256 i; i < methods.length; i++) {
            if (methods[i].id.equals(methodId)) {
                return true;
            }
        }

        return false;
    }
}
