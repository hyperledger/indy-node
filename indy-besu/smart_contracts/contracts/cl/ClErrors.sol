// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @notice Error that occurs when a required field is not provided.
 * @param name The name of the required field.
 */
error FieldRequired(string name);

/**
 * @notice Error that occurs when the specified issuer is not found.
 * @param id Issuer ID.
 */
error IssuerNotFound(string id);

/**
 * @notice Error that occurs when the provided issuer ID is invalid.
 * @param id Issuer ID.
 */
error InvalidIssuerId(string id);

/**
 * @notice Error that occurs when attempting to perform an operation on a deactivated issuer.
 * @param id Issuer ID.
 */
error IssuerHasBeenDeactivated(string id);

// Schema errors

/**
 * @notice Error that occurs when the provided schema ID is invalid.
 * @param id Schema ID.
 */
error InvalidSchemaId(string id);

/**
 * @notice Error that occurs when trying to create an already existing schema.
 * @param id Schema ID.
 */
error SchemaAlreadyExist(string id);

/**
 * @notice Error that occurs when the specified schema is not found.
 * @param id Schema ID.
 */
error SchemaNotFound(string id);

// CredDef errors

/**
 * @notice Error that occurs when the provided credential definition ID is invalid.
 * @param id Credential definition ID.
 */
error InvalidCredentialDefinitionId(string id);

/**
 * @notice Error that occurs when an unsupported credential definition type is used.
 * @param credDefType Credential definition ID.
 */
error UnsupportedCredentialDefinitionType(string credDefType);

/**
 * @notice Error that occurs when trying to create an existing credential definition.
 * @param id Credential definition ID.
 */
error CredentialDefinitionAlreadyExist(string id);

/**
 * @notice Error that occurs when the specified credential definition is not found.
 * @param id Credential definition ID.
 */
error CredentialDefinitionNotFound(string id);

/**
 * @notice Error that occurs when issuer DID of Schema or CredentialDefinition is not owned by sender.
 * @param sender Sender account address.
 * @param owner DID owner account address.
 */
error SenderIsNotIssuerDidOwner(address sender, address owner);
