// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title SchemaWithMetadata
 * @dev This struct holds the details of a schema
 * and its associated metadata.
 *
 * @param schema - The details of the schema.
 * @param metadata - Additional metadata associated with the schema.
 */
struct SchemaWithMetadata {
    Schema schema;
    SchemaMetadata metadata;
}

/**
 * @title Schema
 * @dev This struct holds the essential details of a schema.
 *
 * @param id - Unique identifier for the schema.
 * @param issuerId - Identifier for the issuer of the schema.
 * @param name - Name of the schema.
 * @param version - Version of the schema.
 * @param attrNames - Array of attribute names defined in the schema.
 */
struct Schema {
    string id;
    string issuerId;
    string name;
    string version;
    string[] attrNames;
}

/**
 * @title SchemaMetadata
 * @dev This struct holds additional metadata for a schema.
 *
 * @param created - Timestamp indicating when the schema was created.
 */
struct SchemaMetadata {
    uint256 created;
}
