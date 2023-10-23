// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

error FieldRequired(string name);
error IssuerNotFound(string id);
error IssuerHasBeenDeactivated(string id);

// Schema errors
error InvalidSchemaId(string id);
error SchemaAlreadyExist(string id);
error SchemaNotFound(string id);

// CredDef errors
error InvalidCredentialDefinitionId(string id);
error UnsupportedCredentialDefintionType(string credDefType);
error CredentialDefinitionAlreadyExist(string id);
error CredentialDefinitionNotFound(string id);