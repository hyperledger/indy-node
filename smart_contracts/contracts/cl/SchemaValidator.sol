// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { FieldRequired, InvalidSchemaId } from "./ErrorTypes.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaWithMetadata } from "./SchemaTypes.sol";

using { toSlice } for string;

library SchemaValidator {
    string private constant DELIMITER = "/";
    string private constant SCHEMA_ID_MIDDLE_PART = "/anoncreds/v0/SCHEMA/";

    function requireName(Schema memory self) internal pure {
        if (self.name.toSlice().isEmpty()) revert FieldRequired("name");
    }

    function requireVersion(Schema memory self) internal pure {
        if (self.version.toSlice().isEmpty()) revert FieldRequired("version");
    }

    function requireAttributes(Schema memory self) internal pure {
        if (self.attrNames.length == 0) revert FieldRequired("attributes");
    }

    function requireValidId(Schema memory self) internal pure {
        string memory schemaId = string.concat(self.issuerId, SCHEMA_ID_MIDDLE_PART, self.name, DELIMITER, self.version);

        if (!schemaId.toSlice().eq(self.id.toSlice())) revert InvalidSchemaId(self.id);
    }
}