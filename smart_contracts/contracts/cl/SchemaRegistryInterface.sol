// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Schema, SchemaWithMetadata } from "./SchemaTypes.sol";

interface SchemaRegistryInterface {
    function createSchema(Schema calldata schema) external returns (string memory outId);

    function resolveSchema(string calldata id) external returns (SchemaWithMetadata memory schemaWithMetadata);
}
