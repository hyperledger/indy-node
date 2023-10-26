// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import {toSlice} from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import {FieldRequired, InvalidSchemaId} from "./ClErrors.sol";
import {Schema} from "./SchemaTypes.sol";

using {toSlice} for string;

library SchemaValidator {
    string private constant _DELIMITER = "/";
    string private constant _SCHEMA_ID_MIDDLE_PART = "/anoncreds/v0/SCHEMA/";

    /**
     * @dev Validates the Schema syntax
     */
    function requireValidId(Schema memory self) internal pure {
        string memory schemaId = string.concat(
            self.issuerId,
            _SCHEMA_ID_MIDDLE_PART,
            self.name,
            _DELIMITER,
            self.version
        );

        if (!schemaId.toSlice().eq(self.id.toSlice())) revert InvalidSchemaId(self.id);
    }

    /**
     * @dev Validates that the Schema name is provided
     */
    function requireName(Schema memory self) internal pure {
        if (self.name.toSlice().isEmpty()) revert FieldRequired("name");
    }

    /**
     * @dev Validates that the Schema version is provided
     */
    function requireVersion(Schema memory self) internal pure {
        if (self.version.toSlice().isEmpty()) revert FieldRequired("version");
    }

    /**
     * @dev Validates that the Schema attributes are provided
     */
    function requireAttributes(Schema memory self) internal pure {
        if (self.attrNames.length == 0) revert FieldRequired("attributes");
    }
}
