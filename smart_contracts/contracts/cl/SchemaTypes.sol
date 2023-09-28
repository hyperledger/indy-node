// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

struct Schema {
    SchemaData data;
    SchemaMetadata metadata;
}

struct SchemaData {
    string id;
    string issuerId;
    string name;
    string version;
    string[] attrNames;
}

struct SchemaMetadata {
    uint256 created;
}