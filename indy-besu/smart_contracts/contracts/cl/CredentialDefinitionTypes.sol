// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title CredentialDefinitionWithMetadata
 * @dev This struct holds the details of a credential definition
 * and its associated metadata.
 *
 * @param credDef - The details of the credential definition.
 * @param metadata - Additional metadata associated with the credential definition.
 */
struct CredentialDefinitionWithMetadata {
    CredentialDefinition credDef;
    CredentialDefinitionMetadata metadata;
}

/**
 * @title CredentialDefinition
 * @dev This struct holds the essential details of a credential definition.
 *
 * @param id - Unique identifier for the credential definition.
 * @param issuerId - Identifier for the issuer of the credential.
 * @param schemaId - Identifier for the schema associated with this credential definition.
 * @param credDefType - Type or of the credential definition.
 * @param tag - A tag or label associated with the credential definition.
 * @param value - The value of the credential definition.
 */
struct CredentialDefinition {
    string id;
    string issuerId;
    string schemaId;
    string credDefType;
    string tag;
    string value;
}

/**
 * @title CredentialDefinitionMetadata
 * @dev This struct holds additional metadata for a credential definition.
 *
 * @param created - Timestamp indicating when the credential definition was created.
 */
struct CredentialDefinitionMetadata {
    uint256 created;
}
