// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface SchemaRegistryInterface {
    struct Schema {
        string name;
    }

    function create(string calldata id, Schema calldata schema) external returns (string memory outId);

    function resolve(string calldata id) external returns (Schema memory schema);
}
