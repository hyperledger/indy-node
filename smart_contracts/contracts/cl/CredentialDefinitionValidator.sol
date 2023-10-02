// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { FieldRequired, UnsupportedCredentialDefintionType } from "./ErrorTypes.sol";
import { CredentialDefinitionData } from "./CredentialDefinitionTypes.sol";
import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";

using { toSlice } for string;

library CredentialDefinitionValidator {
    string private constant DELIMITER = "/";
    string private constant CRED_DEF_ID_MIDDLE_PART = "/anoncreds/v0/CLAIM_DEF/";
    string private constant ANONCREDS_TYPE = "CL";
    
    function requireValidId(CredentialDefinitionData memory self) public pure {
    }

    function requireValidType(CredentialDefinitionData memory self) public pure {
        if (self.entityType.toSlice().eq(ANONCREDS_TYPE.toSlice())) {
            revert UnsupportedCredentialDefintionType(self.entityType);
        }
    }

    function requireTag(CredentialDefinitionData memory self) public pure {
        if (self.tag.toSlice().isEmpty()) revert FieldRequired("tag"); 
    }

     function requireValue(CredentialDefinitionData memory self) public pure {
        if (self.value.toSlice().isEmpty()) revert FieldRequired("value"); 
    }
}