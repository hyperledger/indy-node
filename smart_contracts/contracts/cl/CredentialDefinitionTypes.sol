// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

struct CredentialDefinitionWithMetadata {
    CredentialDefinition credDef;
    CredentialDefinitionMetadata metadata;
}

struct CredentialDefinition {
    string id;
    string issuerId;
    string schemaId;
    string credDefType;
    string tag;
    string value;
}

struct CredentialDefinitionMetadata {
    uint256 created;
}