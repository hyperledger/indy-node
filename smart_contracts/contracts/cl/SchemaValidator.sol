// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import { Schema, SchemaData } from "./SchemaTypes.sol";
import { DidValidator } from "../did/DidValidator.sol";

using { toSlice } for string;

library SchemaValidator {
    string private constant DELIMITER = "/";
    string private constant SCHEMA_ID_MIDDLE_PART = "/anoncreds/v0/SCHEMA/";

    function requireName(SchemaData memory schema) public pure {
        if (schema.name.toSlice().isEmpty()) revert SchemaRegistryInterface.FieldRequired("name");
    }

    function requireVersion(SchemaData memory schema) public pure {
        if (schema.version.toSlice().isEmpty()) revert SchemaRegistryInterface.FieldRequired("version");
    }

    function requireAttributes(SchemaData memory schema) public pure {
        if (schema.attrNames.length == 0) revert SchemaRegistryInterface.FieldRequired("attributes");
    }

    function requireValidSchemaId(SchemaData memory schema) public pure {
        string memory schemaId = string.concat(schema.issuerId, SCHEMA_ID_MIDDLE_PART, schema.name, DELIMITER, schema.version);

        if (!schemaId.toSlice().eq(schema.id.toSlice())) revert SchemaRegistryInterface.InvalidSchemId(schema.id);
    }
}