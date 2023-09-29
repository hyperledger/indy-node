// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { Schema, SchemaData } from "./SchemaTypes.sol";

interface SchemaRegistryInterface {

    error IssuerNotFound(string id);
    error InvalidSchemId(string id);
    error SchemaIdExist(string id);
    error SchemaNotFound(string id);
    error FieldRequired(string name);

    function createSchema(SchemaData calldata data) external returns (string memory outId);

    function resolveSchema(string calldata id) external returns (Schema memory schema);
}
