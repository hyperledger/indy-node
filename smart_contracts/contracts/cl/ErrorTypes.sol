// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

error FieldRequired(string name);
error IssuerNotFound(string id);

// Schema errors
error InvalidSchemId(string id);
error SchemaIdExist(string id);
error SchemaNotFound(string id);

// CredDef errors
error UnsupportedCredentialDefintionType(string entityType);
error CredentialDefinitionIdExist(string id);
error CredentialDefinitionNotFound(string id);