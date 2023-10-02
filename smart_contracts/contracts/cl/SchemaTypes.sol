// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

struct SchemaWithMetadata {
    Schema schema;
    SchemaMetadata metadata;
}

struct Schema {
    string id;
    string issuerId;
    string name;
    string version;
    string[] attrNames;
}

struct SchemaMetadata {
    uint256 created;
}
