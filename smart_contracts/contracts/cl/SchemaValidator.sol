// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { Schema, SchemaData } from "./SchemaTypes.sol";
import { DidValidator } from "../did/DidValidator.sol";

using { toSlice } for string;

library SchemaValidator {
    string private constant DELIMITER = "/";
    string private constant SCHEMA_ID_MIDDLE_PART = "/anoncreds/v0/SCHEMA/";

    function requireName(SchemaData memory schema) public pure {
        require(!schema.name.toSlice().isEmpty(), "Schema name is required");
    }

    function requireVersion(SchemaData memory schema) public pure {
        require(!schema.version.toSlice().isEmpty(), "Schema version is required");
    }

    function requireAttributes(SchemaData memory schema) public pure {
        require(schema.attrNames.length != 0, "Schema must contain at least one attribute");
    }

    function requireValidSchemaId(SchemaData memory schema) public pure {
        string memory schemaId = string.concat(schema.issuerId, SCHEMA_ID_MIDDLE_PART, schema.name, DELIMITER, schema.version);

        require(schemaId.toSlice().eq(schema.id.toSlice()), 'Incorrect schema id');
    }
}