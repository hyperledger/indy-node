// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StringUtils } from "../utils/StringUtils.sol";
import { FieldRequired, InvalidCredentialDefinitionId, UnsupportedCredentialDefinitionType } from "./ClErrors.sol";
import { CredentialDefinition } from "./CredentialDefinitionTypes.sol";

using StringUtils for string;

library CredentialDefinitionValidator {
    string private constant _DELIMITER = "/";
    string private constant _CRED_DEF_ID_MIDDLE_PART = "/anoncreds/v0/CLAIM_DEF/";
    string private constant _ANONCREDS_TYPE = "CL";

    /**
     * @dev Validates the Credential Definition syntax
     */
    function requireValidId(CredentialDefinition memory self) internal pure {
        string memory credDefId = string.concat(
            self.issuerId,
            _CRED_DEF_ID_MIDDLE_PART,
            self.schemaId,
            _DELIMITER,
            self.tag
        );

        if (!credDefId.equals(self.id)) revert InvalidCredentialDefinitionId(self.id);
    }

    /**
     * @dev Validates the Credential Definition type
     */
    function requireValidType(CredentialDefinition memory self) internal pure {
        if (!self.credDefType.equals(_ANONCREDS_TYPE)) {
            revert UnsupportedCredentialDefinitionType(self.credDefType);
        }
    }

    /**
     * @dev Validates that the Credential Definition tag is provided
     */
    function requireTag(CredentialDefinition memory self) internal pure {
        if (self.tag.isEmpty()) revert FieldRequired("tag");
    }

    /**
     * @dev Validates that the Credential Definition value is provided
     */
    function requireValue(CredentialDefinition memory self) internal pure {
        if (self.value.isEmpty()) revert FieldRequired("value");
    }
}
